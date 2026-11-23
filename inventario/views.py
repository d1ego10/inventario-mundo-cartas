from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from usuarios.models import Perfil
from .models import Categoria
from .forms import CategoriaForm
from django.db.models import Q
from .models import Producto, MovimientoInventario
from .forms import ProductoForm
from django.db import transaction
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
def listar_productos(request):
    productos = Producto.objects.filter(
        activo=True
    ).select_related("categoria")

    buscar = request.GET.get("buscar", "")

    if buscar:
        productos = productos.filter(
            Q(nombre__icontains=buscar) |
            Q(sku__icontains=buscar)
        )

    productos = productos.order_by("nombre")

    es_admin = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador"
    ).exists()

    return render(request, "inventario/producto_listar.html", {
        "productos": productos,
        "es_admin": es_admin,
        "buscar": buscar,
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