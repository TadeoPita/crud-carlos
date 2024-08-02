from django import forms
from .models import Entrada, Salida, Tarea, Inventario

class EntradaForm(forms.ModelForm):
    codigo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    
    class Meta:
        model = Entrada
        fields = ['codigo', 'descripcion', 'cantidad', 'fecha', 'color', 'bolsas']
        widgets = {
            'fecha': forms.DateInput(format='%d/%m/%Y', attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'bolsas': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SalidaForm(forms.ModelForm):
    codigo = forms.ModelChoiceField(queryset=Inventario.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Salida
        fields = ['codigo', 'descripcion', 'cantidad', 'fecha', 'obra']
        widgets = {
            'fecha': forms.DateInput(format='%d/%m/%Y', attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'obra': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'fecha_entrega', 'prioridad', 'completada', 'asignada_a']
        widgets = {
            'fecha_entrega': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'prioridad': forms.TextInput(attrs={'class': 'form-control'}),
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'asignada_a': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
