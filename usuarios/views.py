from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from .models import Perfil
from django.db import transaction
from .forms import CrearUsuarioForm

# Create your views here.



def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("inventario:inicio")

    form = AuthenticationForm(
        request=request,
        data=request.POST if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("inventario:inicio")

    return render(request, "usuarios/login.html", {"form": form})


@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect("usuarios:login")

@login_required
def listar_usuarios(request):
    es_administrador = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador",
    ).exists()

    if not es_administrador:
        raise PermissionDenied

    usuarios = (
        get_user_model().objects
        .filter(is_superuser=False)
        .select_related("perfil__rol")
        .order_by("username")
    )

    return render(
        request,
        "usuarios/usuario_listar.html",
        {"usuarios": usuarios},
    )
    
@login_required
def crear_usuario(request):
    es_administrador = Perfil.objects.filter(
        user=request.user,
        rol__nombre="Administrador",
    ).exists()

    if not es_administrador:
        raise PermissionDenied

    form = CrearUsuarioForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            usuario = form.save()

            Perfil.objects.create(
                user=usuario,
                rol=form.cleaned_data["rol"],
            )

        return redirect("usuarios:listar")

    return render(
        request,
        "usuarios/usuario_form.html",
        {"form": form},
    )