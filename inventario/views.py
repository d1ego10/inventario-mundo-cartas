from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from usuarios.models import Perfil
from .models import Categoria
from .forms import CategoriaForm
from django.db.models import Q, F
from .models import Categoria, Producto, MovimientoInventario
from .forms import ProductoForm
from django.db import transaction
from django.views.decorators.http import require_POST
from .forms import ProductoEditarForm
from .forms import MovimientoForm
# Create your views here.

@login_required
def inicio(request):
    return render(request, "inventario/inicio.html")

def verificar_admin(request):
    es_admin = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador"
    ).exists()

    if not es_admin:
        raise PermissionDenied


@login_required
def listar_categorias(request):
    verificar_admin(request)

    categorias = Categoria.objects.all().order_by("nombre")

    return render(request, "inventario/categoria_listar.html", {
        "categorias": categorias
    })


@login_required
def crear_categoria(request):
    verificar_admin(request)

    form = CategoriaForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventario:categorias")

    return render(request, "inventario/categoria_form.html", {
        "form": form
    })


@login_required
def editar_categoria(request, pk):
    verificar_admin(request)

    categoria = get_object_or_404(Categoria, pk=pk)

    form = CategoriaForm(
        request.POST if request.method == "POST" else None,
        instance=categoria
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventario:categorias")

    return render(request, "inventario/categoria_form.html", {
        "form": form
    })


@login_required
def detalle_producto(request, pk):
    es_admin = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador"
    ).exists()

    productos = Producto.objects.select_related("categoria")

    if not es_admin:
        productos = productos.filter(activo=True)

    producto = get_object_or_404(productos, pk=pk)

    movimientos = producto.movimientos.select_related(
        "usuario"
    ).order_by("-fecha", "-id")

    return render(request, "inventario/producto_detalle.html", {
        "producto": producto,
        "movimientos": movimientos,
    })


@login_required
def crear_producto(request):
    verificar_admin(request)

    form = ProductoForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            producto = form.save(commit=False)
            stock = form.cleaned_data["stock_inicial"]
            producto.stock_actual = stock
            producto.save()

            if stock > 0:
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo="ENTRADA",
                    cantidad=stock,
                    motivo="Stock inicial",
                    stock_resultante=stock,
                    usuario=request.user,
                )

        return redirect("inventario:productos")

    return render(request, "inventario/producto_form.html", {
        "form": form
    })
    
    

@login_required
def editar_producto(request, pk):
    verificar_admin(request)

    producto = get_object_or_404(Producto, pk=pk, activo=True)

    form = ProductoEditarForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=producto
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventario:productos")

    return render(request, "inventario/producto_form.html", {
        "form": form,
        "editando": True,
    })


@login_required
@require_POST
def desactivar_producto(request, pk):
    verificar_admin(request)

    producto = get_object_or_404(Producto, pk=pk, activo=True)
    producto.activo = False
    producto.save()

    return redirect("inventario:productos")


@login_required
def registrar_movimiento(request):
    verificar_admin(request)

    form = MovimientoForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():

        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(
                pk=form.cleaned_data["producto"].pk,
                activo=True
            )

            tipo = form.cleaned_data["tipo"]
            cantidad = form.cleaned_data["cantidad"]
            motivo = form.cleaned_data["motivo"]

            if tipo == "SALIDA" and cantidad > producto.stock_actual:
                form.add_error(
                    "cantidad",
                    "No hay stock suficiente para esta salida."
                )
            else:
                if tipo == "ENTRADA":
                    producto.stock_actual += cantidad
                else:
                    producto.stock_actual -= cantidad

                producto.save(update_fields=["stock_actual"])

                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo=tipo,
                    cantidad=cantidad,
                    motivo=motivo,
                    stock_resultante=producto.stock_actual,
                    usuario=request.user
                )

                return redirect("inventario:movimientos")

    return render(request, "inventario/movimiento_form.html", {
        "form": form
    })


@login_required
def listar_movimientos(request):
    verificar_admin(request)

    movimientos = MovimientoInventario.objects.select_related(
        "producto", "usuario"
    ).order_by("-fecha", "-id")

    return render(request, "inventario/movimiento_listar.html", {
        "movimientos": movimientos
    })
    
@login_required
def listar_productos(request):
    es_admin = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador"
    ).exists()

    productos = Producto.objects.select_related("categoria")

    if not es_admin:
        productos = productos.filter(activo=True)

    buscar = request.GET.get("buscar", "").strip()
    categoria = request.GET.get("categoria", "")
    estado = request.GET.get("estado", "")

    if buscar:
        productos = productos.filter(
            Q(nombre__icontains=buscar) |
            Q(sku__icontains=buscar)
        )

    categoria_id = int(categoria) if categoria.isdigit() else None

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if estado == "agotado":
        productos = productos.filter(
            activo=True,
            stock_actual=0
        )
    elif estado == "bajo":
        productos = productos.filter(
            activo=True,
            stock_actual__gt=0,
            stock_actual__lte=F("stock_minimo")
        )
    elif estado == "disponible":
        productos = productos.filter(
            activo=True,
            stock_actual__gt=F("stock_minimo")
        )

    return render(request, "inventario/producto_listar.html", {
        "productos": productos.order_by("nombre"),
        "categorias": Categoria.objects.all().order_by("nombre"),
        "es_admin": es_admin,
        "buscar": buscar,
        "categoria_seleccionada": categoria_id,
        "estado_seleccionado": estado,
    })