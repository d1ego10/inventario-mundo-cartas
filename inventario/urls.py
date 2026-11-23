from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("categorias/", views.listar_categorias, name="categorias"),
    path("categorias/crear/", views.crear_categoria, name="categoria_crear"),
    path("categorias/editar/<int:pk>/", views.editar_categoria, name="categoria_editar"),
]