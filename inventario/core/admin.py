# core/admin.py
from django.contrib import admin
from .models import Entrada, Salida, Inventario, Tarea

# Register your models here.
admin.site.register(Entrada)
admin.site.register(Salida)
admin.site.register(Inventario)
admin.site.register(Tarea)