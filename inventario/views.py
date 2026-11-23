from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from usuarios.models import Perfil
from .models import Categoria
from .forms import CategoriaForm
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