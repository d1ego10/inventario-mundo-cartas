from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path("", views.nueva_venta, name="nueva"),
    path("agregar/<int:pk>/", views.agregar_producto, name="agregar"),
    path("actualizar/<int:pk>/", views.actualizar_carrito, name="actualizar"),
    path("quitar/<int:pk>/", views.quitar_producto, name="quitar"),
    path("confirmar/", views.confirmar_venta, name="confirmar"),
]