from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("categorias/", views.listar_categorias, name="categorias"),
    path("categorias/crear/", views.crear_categoria, name="categoria_crear"),
    path("categorias/editar/<int:pk>/", views.editar_categoria, name="categoria_editar"),
    path("productos/", views.listar_productos, name="productos"),
    path("productos/crear/", views.crear_producto, name="producto_crear"),
    path("productos/editar/<int:pk>/", views.editar_producto, name="producto_editar"),
    path("productos/desactivar/<int:pk>/", views.desactivar_producto, name="producto_desactivar"),
    path("mercaderia/", views.registrar_movimiento, name="mercaderia"),
    path("movimientos/", views.listar_movimientos, name="movimientos"),
    path("productos/<int:pk>/", views.detalle_producto, name="producto_detalle"),
]