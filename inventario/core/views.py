from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Entrada, Salida, Inventario, Tarea
from .forms import EntradaForm, SalidaForm, TareaForm
from django.http import HttpResponse
import csv
from django.db.models import Q
from django.utils.dateparse import parse_date

@login_required
def buscar(request):
    query = request.GET.get('q')
    fecha_query = request.GET.get('fecha')
    cantidad_query = request.GET.get('cantidad')

    entradas = Entrada.objects.all()
    salidas = Salida.objects.all()
    tareas = Tarea.objects.all()
    inventarios = Inventario.objects.all()

    if query:
        entradas = entradas.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query))
        salidas = salidas.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query))
        tareas = tareas.filter(Q(titulo__icontains=query) | Q(descripcion__icontains=query))
        inventarios = inventarios.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query))

    if fecha_query:
        try:
            fecha = parse_date(fecha_query)
            if fecha:
                entradas = entradas.filter(fecha=fecha)
                salidas = salidas.filter(fecha=fecha)
                tareas = tareas.filter(fecha_entrega=fecha)
        except ValueError:
            pass  # Manejo de error si la fecha no es válida

    if cantidad_query:
        try:
            cantidad = int(cantidad_query)
            entradas = entradas.filter(cantidad=cantidad)
            salidas = salidas.filter(cantidad=cantidad)
            inventarios = inventarios.filter(inventario=cantidad)
        except ValueError:
            pass  # Manejo de error si la cantidad no es un número válido

    context = {
        'entradas': entradas,
        'salidas': salidas,
        'tareas': tareas,
        'inventarios': inventarios,
        'query': query,
        'fecha_query': fecha_query,
        'cantidad_query': cantidad_query,
    }
    return render(request, 'core/buscar.html', context)

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventario.csv"'

    writer = csv.writer(response)
    writer.writerow(['Tipo', 'Código', 'Descripción', 'Cantidad'])

    entradas = Entrada.objects.all()
    for entrada in entradas:
        writer.writerow(['Entrada', entrada.codigo, entrada.descripcion, entrada.cantidad])

    salidas = Salida.objects.all()
    for salida in salidas:
        writer.writerow(['Salida', salida.codigo, salida.descripcion, salida.cantidad])

    inventarios = Inventario.objects.all()
    for inventario in inventarios:
        writer.writerow(['Inventario', inventario.codigo, inventario.descripcion, inventario.inventario])

    return response

def home(request):
    return render(request, 'core/home.html')

def is_admin(user):
    return user.is_staff

def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(is_admin)(view_func))
    return decorated_view_func

@admin_required
def entrada_create(request):
    if request.method == 'POST':
        form = EntradaForm(request.POST)
        if form.is_valid():
            entrada = form.save()
            inventario, created = Inventario.objects.get_or_create(codigo=entrada.codigo, defaults={
                'descripcion': entrada.descripcion,
                'entradas': 0,
                'salidas': 0,
                'inventario': 0,
                'fecha': entrada.fecha,
                'color': entrada.color,
                'bolsas': entrada.bolsas
            })
            inventario.entradas += entrada.cantidad
            inventario.inventario += entrada.cantidad
            if not created:
                inventario.descripcion = entrada.descripcion
                inventario.fecha = entrada.fecha
                inventario.color = entrada.color
                inventario.bolsas = entrada.bolsas
            inventario.save()
            return redirect('entrada_list')
    else:
        form = EntradaForm()
    inventarios = Inventario.objects.all()
    return render(request, 'core/entrada_form.html', {'form': form, 'inventarios': inventarios})


@admin_required
def entrada_edit(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk)
    cantidad_original = entrada.cantidad
    codigo_original = entrada.codigo

    if request.method == 'POST':
        form = EntradaForm(request.POST, instance=entrada)
        if form.is_valid():
            entrada = form.save(commit=False)
            diferencia = entrada.cantidad - cantidad_original

            if codigo_original != entrada.codigo:
                # Actualizar el inventario original
                try:
                    inventario_original = Inventario.objects.get(codigo=codigo_original)
                    inventario_original.entradas -= cantidad_original
                    inventario_original.inventario -= cantidad_original
                    inventario_original.save()
                except Inventario.DoesNotExist:
                    inventario_original = None

                # Verificar si existe inventario con el nuevo código
                try:
                    inventario = Inventario.objects.get(codigo=entrada.codigo)
                except Inventario.DoesNotExist:
                    inventario = Inventario(
                        codigo=entrada.codigo,
                        descripcion=entrada.descripcion,
                        entradas=0,
                        salidas=0,
                        inventario=0,
                        fecha=entrada.fecha,
                        color=entrada.color,
                        bolsas=entrada.bolsas
                    )

                inventario.entradas += entrada.cantidad
                inventario.inventario += entrada.cantidad
                inventario.descripcion = entrada.descripcion
                inventario.fecha = entrada.fecha
                inventario.color = entrada.color
                inventario.bolsas = entrada.bolsas
                inventario.save()
            else:
                # Actualizar el inventario existente
                inventario = Inventario.objects.get(codigo=entrada.codigo)
                inventario.descripcion = entrada.descripcion
                inventario.entradas += diferencia
                inventario.inventario += diferencia
                inventario.fecha = entrada.fecha
                inventario.color = entrada.color
                inventario.bolsas = entrada.bolsas
                inventario.save()

            entrada.save()
            return redirect('entrada_list')
    else:
        form = EntradaForm(instance=entrada)
    return render(request, 'core/entrada_form.html', {'form': form})



@admin_required
def entrada_delete(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk)
    if request.method == 'POST':
        inventario = Inventario.objects.get(codigo=entrada.codigo)
        inventario.entradas -= entrada.cantidad
        inventario.inventario -= entrada.cantidad
        inventario.save()
        entrada.delete()
        return redirect('entrada_list')
    return render(request, 'core/entrada_confirm_delete.html', {'object': entrada})

@admin_required
def salida_create(request):
    if request.method == 'POST':
        form = SalidaForm(request.POST)
        if form.is_valid():
            salida = form.save(commit=False)
            try:
                inventario = Inventario.objects.get(codigo=salida.codigo)
                if inventario.inventario >= salida.cantidad:
                    inventario.salidas += salida.cantidad
                    inventario.inventario -= salida.cantidad
                    inventario.save()
                    salida.save()
                else:
                    form.add_error('cantidad', 'No hay suficiente cantidad en el inventario.')
            except Inventario.DoesNotExist:
                form.add_error('codigo', 'No hay inventario para el código proporcionado.')
            return redirect('salida_list')
    else:
        form = SalidaForm()
    inventarios = Inventario.objects.all()
    return render(request, 'core/salida_form.html', {'form': form, 'inventarios': inventarios})

@admin_required
def salida_edit(request, pk):
    salida = get_object_or_404(Salida, pk=pk)
    cantidad_original = salida.cantidad
    codigo_original = salida.codigo

    if request.method == 'POST':
        form = SalidaForm(request.POST, instance=salida)
        if form.is_valid():
            salida = form.save(commit=False)
            diferencia = salida.cantidad - cantidad_original

            if codigo_original != salida.codigo:
                # Actualizar el inventario original
                try:
                    inventario_original = Inventario.objects.get(codigo=codigo_original)
                    inventario_original.salidas -= cantidad_original
                    inventario_original.inventario += cantidad_original
                    inventario_original.save()
                except Inventario.DoesNotExist:
                    inventario_original = None

                # Verificar si existe inventario con el nuevo código
                try:
                    inventario = Inventario.objects.get(codigo=salida.codigo)
                    inventario.salidas += salida.cantidad
                    inventario.inventario -= salida.cantidad
                except Inventario.DoesNotExist:
                    inventario = Inventario(
                        codigo=salida.codigo,
                        descripcion=salida.descripcion,
                        entradas=0,
                        salidas=salida.cantidad,
                        inventario=-salida.cantidad
                    )
                inventario.descripcion = salida.descripcion
                inventario.save()
            else:
                # Actualizar el inventario existente
                inventario = Inventario.objects.get(codigo=salida.codigo)
                inventario.descripcion = salida.descripcion
                inventario.salidas += diferencia
                inventario.inventario -= diferencia
                inventario.save()

            salida.save()
            return redirect('salida_list')
    else:
        form = SalidaForm(instance=salida)
    return render(request, 'core/salida_form.html', {'form': form, 'inventarios': Inventario.objects.all()})


@admin_required
def salida_delete(request, pk):
    salida = get_object_or_404(Salida, pk=pk)
    if request.method == 'POST':
        inventario = Inventario.objects.get(codigo=salida.codigo)
        inventario.salidas -= salida.cantidad
        inventario.inventario += salida.cantidad
        inventario.save()
        salida.delete()
        return redirect('salida_list')
    return render(request, 'core/salida_confirm_delete.html', {'object': salida})

@admin_required
def tarea_create(request):
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.creado_por = request.user  # Asignar el usuario actual como creador
            tarea.save()
            form.save_m2m()  # Guardar las relaciones ManyToMany después de guardar el objeto
            return redirect('tarea_list')
    else:
        form = TareaForm()
    return render(request, 'core/tarea_form.html', {'form': form})


@login_required
def entrada_list(request):
    query = request.GET.get('q')
    if query:
        entradas = Entrada.objects.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query))
    else:
        entradas = Entrada.objects.all()
    return render(request, 'core/entrada_list.html', {'entradas': entradas, 'query': query})

@login_required
def salida_list(request):
    query = request.GET.get('q')
    if query:
        salidas = Salida.objects.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query))
    else:
        salidas = Salida.objects.all()
    return render(request, 'core/salida_list.html', {'salidas': salidas, 'query': query})

@login_required
def tarea_list(request):
    query = request.GET.get('q')
    if query:
        tareas = Tarea.objects.filter(Q(titulo__icontains=query) | Q(descripcion__icontains=query))
    else:
        tareas = Tarea.objects.all()
    return render(request, 'core/tarea_list.html', {'tareas': tareas, 'query': query})

@login_required
def inventario_list(request):
    query = request.GET.get('q')
    if query:
        inventarios = Inventario.objects.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query))
    else:
        inventarios = Inventario.objects.all()
    return render(request, 'core/inventario_list.html', {'inventarios': inventarios, 'query': query})
