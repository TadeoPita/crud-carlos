# Generated by Django 4.2.7 on 2024-07-26 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_inventario_entradas_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entrada',
            name='bolsas',
            field=models.CharField(max_length=50),
        ),
    ]
