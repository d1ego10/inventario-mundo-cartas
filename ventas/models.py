from django.db import models
from django.conf import settings
from inventario.models import Producto

# Create your models here.

class Venta(models.Model):
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )
    anulada = models.BooleanField(default=False)
    motivo_anulacion = models.TextField(blank=True)

    def __str__(self):
        return f"Venta #{self.id}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"