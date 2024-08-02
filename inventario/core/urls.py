from django.urls import path
from .views import entrada_list, entrada_create, entrada_edit, entrada_delete, salida_list, salida_create, salida_edit, salida_delete, tarea_list, tarea_create, buscar, inventario_list, home
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('entradas/', entrada_list, name='entrada_list'),
    path('entradas/nueva/', entrada_create, name='entrada_create'),
    path('entradas/editar/<int:pk>/', entrada_edit, name='entrada_edit'),
    path('entradas/borrar/<int:pk>/', entrada_delete, name='entrada_delete'),
    path('salidas/', salida_list, name='salida_list'),
    path('salidas/nueva/', salida_create, name='salida_create'),
    path('salidas/editar/<int:pk>/', salida_edit, name='salida_edit'),
    path('salidas/borrar/<int:pk>/', salida_delete, name='salida_delete'),
    path('tareas/', tarea_list, name='tarea_list'),
    path('tareas/nueva/', tarea_create, name='tarea_create'),
    path('inventario/', inventario_list, name='inventario_list'),
    path('buscar/', buscar, name='buscar'),
    path('export-csv/', views.export_csv, name='export_csv'),
]
