from django.db import models
from django.contrib.auth.models import User

class Entrada(models.Model):
    codigo = models.CharField(max_length=50)
    descripcion = models.TextField()
    cantidad = models.IntegerField()
    fecha = models.DateField()
    color = models.CharField(max_length=50)
    bolsas = models.CharField(max_length=50)  # Cambiado a texto

    def __str__(self):
        return self.codigo

class Salida(models.Model):
    codigo = models.CharField(max_length=50)
    descripcion = models.TextField()
    cantidad = models.IntegerField()
    fecha = models.DateField()
    obra = models.CharField(max_length=100)

    def __str__(self):
        return self.codigo

class Inventario(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()
    entradas = models.IntegerField(default=0)
    salidas = models.IntegerField(default=0)
    inventario = models.IntegerField(default=0)
    fecha = models.DateField(null=True, blank=True)  # Agregar campo fecha
    color = models.CharField(max_length=50, null=True, blank=True)  # Agregar campo color
    bolsas = models.CharField(max_length=50, null=True, blank=True)  # Agregar campo bolsas

    def __str__(self):
        return self.codigo


class Tarea(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_entrega = models.DateField()
    prioridad = models.CharField(max_length=50)
    completada = models.BooleanField(default=False)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_creadas')
    asignada_a = models.ManyToManyField(User, related_name='tareas_asignadas')

    def __str__(self):
        return self.titulo
