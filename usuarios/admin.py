from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Rol, Perfil


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "rol")
    list_filter = ("rol",)
    search_fields = ("user__username",)