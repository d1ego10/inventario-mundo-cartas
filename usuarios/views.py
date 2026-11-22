from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST


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