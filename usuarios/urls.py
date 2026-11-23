from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.listar_usuarios, name="listar"),
    path("crear/", views.crear_usuario, name="crear"),
    path("login/", views.iniciar_sesion, name="login"),
    path("logout/", views.cerrar_sesion, name="logout"),
]