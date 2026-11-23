from django import forms
from .models import Categoria
from .models import Producto
from .models import MovimientoInventario, Producto

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }

class ProductoForm(forms.ModelForm):
    stock_inicial = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Stock inicial"
    )

    class Meta:
        model = Producto
        fields = [
            "nombre",
            "variante",
            "sku",
            "categoria",
            "unidad_venta",
            "precio",
            "stock_minimo",
            "imagen",
        ]
        labels = {
            "variante": "Variante o edición",
            "sku": "Código SKU",
            "unidad_venta": "Unidad de venta",
            "stock_minimo": "Stock mínimo",
            "imagen": "Imagen (opcional)",
        }
#para nuev form
class ProductoEditarForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "variante",
            "sku",
            "categoria",
            "unidad_venta",
            "precio",
            "stock_minimo",
            "imagen",
        ]

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ["producto", "tipo", "cantidad", "motivo"]

        labels = {
            "producto": "Producto",
            "tipo": "Movimiento",
            "cantidad": "Cantidad de unidades",
            "motivo": "Motivo / referencia",
        }

        widgets = {
            "producto": forms.Select(attrs={"class": "form-select"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "motivo": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["producto"].queryset = Producto.objects.filter(
            activo=True
        ).order_by("nombre")

        self.fields["producto"].label_from_instance = (
            lambda producto: f"{producto.nombre} - {producto.sku} "
                             f"(Stock: {producto.stock_actual})"
        )

