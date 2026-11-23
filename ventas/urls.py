from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path("", views.nueva_venta, name="nueva"),
    path("agregar/<int:pk>/", views.agregar_producto, name="agregar"),
    path("actualizar/<int:pk>/", views.actualizar_carrito, name="actualizar"),
    path("quitar/<int:pk>/", views.quitar_producto, name="quitar"),
    path("confirmar/", views.confirmar_venta, name="confirmar"),
    path("historial/", views.historial_ventas, name="historial"),
    path("historial/<int:pk>/", views.detalle_venta, name="detalle"),
    path("historial/<int:pk>/anular/", views.anular_venta, name="anular"),
]