
from django import forms
from .models import Categoria
from .models import Producto


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
