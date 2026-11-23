from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F

from usuarios.models import Perfil
from inventario.models import Producto, MovimientoInventario
from .models import Venta, DetalleVenta

# Create your views here.
def verificar_vendedor(request):
    permitido = Perfil.objects.filter(
        user=request.user,
        rol__nombre__in=["Administrador", "Vendedor"]
    ).exists()

    if not permitido:
        raise PermissionDenied


@login_required
def nueva_venta(request):
    verificar_vendedor(request)

    productos = Producto.objects.filter(
        activo=True
    ).order_by("nombre")

    carrito = request.session.get("carrito", {})
    items = []
    total = Decimal("0")

    for producto in Producto.objects.filter(
        pk__in=carrito.keys()
    ):
        cantidad = carrito[str(producto.id)]
        subtotal = producto.precio * cantidad

        items.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": subtotal,
        })

        total += subtotal

    return render(request, "ventas/nueva_venta.html", {
        "productos": productos,
        "items": items,
        "total": total,
    })


@login_required
@require_POST
def agregar_producto(request, pk):
    verificar_vendedor(request)

    producto = get_object_or_404(
        Producto, pk=pk, activo=True
    )

    try:
        cantidad = int(request.POST.get("cantidad", 1))
    except ValueError:
        cantidad = 0

    carrito = request.session.get("carrito", {})
    clave = str(pk)
    nueva_cantidad = carrito.get(clave, 0) + cantidad

    if cantidad <= 0:
        messages.error(request, "Cantidad inválida.")
    elif nueva_cantidad > producto.stock_actual:
        messages.error(request, "No hay stock suficiente.")
    else:
        carrito[clave] = nueva_cantidad
        request.session["carrito"] = carrito

    return redirect("ventas:nueva")


@login_required
@require_POST
def actualizar_carrito(request, pk):
    verificar_vendedor(request)

    producto = get_object_or_404(
        Producto, pk=pk, activo=True
    )

    try:
        cantidad = int(request.POST.get("cantidad", 1))
    except ValueError:
        cantidad = 0

    if cantidad <= 0 or cantidad > producto.stock_actual:
        messages.error(request, "Cantidad no disponible.")
    else:
        carrito = request.session.get("carrito", {})
        carrito[str(pk)] = cantidad
        request.session["carrito"] = carrito

    return redirect("ventas:nueva")


@login_required
@require_POST
def quitar_producto(request, pk):
    verificar_vendedor(request)

    carrito = request.session.get("carrito", {})
    carrito.pop(str(pk), None)
    request.session["carrito"] = carrito

    return redirect("ventas:nueva")


@login_required
@require_POST
def confirmar_venta(request):
    verificar_vendedor(request)

    carrito = request.session.get("carrito", {})

    if not carrito:
        messages.error(request, "El carrito está vacío.")
        return redirect("ventas:nueva")

    try:
        with transaction.atomic():
            venta = Venta.objects.create(vendedor=request.user)
            total = Decimal("0")

            for producto_id, cantidad in carrito.items():
                if not isinstance(cantidad, int) or cantidad <= 0:
                    raise ValueError("Cantidad inválida.")

                producto = Producto.objects.get(
                    pk=producto_id,
                    activo=True
                )

                actualizado = Producto.objects.filter(
                    pk=producto.pk,
                    activo=True,
                    stock_actual__gte=cantidad
                ).update(
                    stock_actual=F("stock_actual") - cantidad
                )

                if not actualizado:
                    raise ValueError(
                        f"Stock insuficiente para {producto.nombre}."
                    )

                producto.refresh_from_db()

                subtotal = producto.precio * cantidad

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal,
                )

                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo="SALIDA",
                    cantidad=cantidad,
                    motivo=f"Venta #{venta.id}",
                    stock_resultante=producto.stock_actual,
                    usuario=request.user,
                )

                total += subtotal

            venta.total = total
            venta.save()

    except Producto.DoesNotExist:
        messages.error(
            request,
            "Uno de los productos ya no está disponible."
        )
        return redirect("ventas:nueva")

    except ValueError as error:
        messages.error(request, str(error))
        return redirect("ventas:nueva")

    request.session.pop("carrito", None)

    messages.success(
        request,
        f"Venta #{venta.id} registrada correctamente."
    )

    return redirect("ventas:nueva")

@login_required
def historial_ventas(request):
    verificar_vendedor(request)

    es_admin = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador"
    ).exists()

    ventas = Venta.objects.select_related("vendedor")

    if not es_admin:
        ventas = ventas.filter(vendedor=request.user)

    ventas = ventas.order_by("-fecha", "-id")

    return render(request, "ventas/historial.html", {
        "ventas": ventas,
    })


@login_required
def detalle_venta(request, pk):
    verificar_vendedor(request)

    es_admin = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador"
    ).exists()

    ventas = Venta.objects.select_related("vendedor")

    if not es_admin:
        ventas = ventas.filter(vendedor=request.user)

    venta = get_object_or_404(ventas, pk=pk)

    detalles = venta.detalles.select_related("producto")

    return render(request, "ventas/detalle.html", {
        "venta": venta,
        "detalles": detalles,
        "es_admin": es_admin,
    })

@login_required
@require_POST
def anular_venta(request, pk):
    es_admin = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador"
    ).exists()

    if not es_admin:
        raise PermissionDenied

    motivo = request.POST.get("motivo", "").strip()

    if not motivo:
        messages.error(request, "Debes indicar el motivo de anulación.")
        return redirect("ventas:detalle", pk=pk)

    with transaction.atomic():
        venta = get_object_or_404(
            Venta.objects.select_for_update(),
            pk=pk
        )

        if venta.anulada:
            messages.error(request, "Esta venta ya fue anulada.")
            return redirect("ventas:detalle", pk=pk)

        for detalle in venta.detalles.select_related("producto"):
            producto = detalle.producto

            Producto.objects.filter(pk=producto.pk).update(
                stock_actual=F("stock_actual") + detalle.cantidad
            )

            producto.refresh_from_db()

            MovimientoInventario.objects.create(
                producto=producto,
                tipo="ENTRADA",
                cantidad=detalle.cantidad,
                motivo=f"Anulación venta #{venta.id}: {motivo}",
                stock_resultante=producto.stock_actual,
                usuario=request.user,
            )

        venta.anulada = True
        venta.motivo_anulacion = motivo
        venta.save(update_fields=["anulada", "motivo_anulacion"])

    messages.success(request, "Venta anulada correctamente.")
    return redirect("ventas:detalle", pk=pk)