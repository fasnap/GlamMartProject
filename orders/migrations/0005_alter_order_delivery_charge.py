# Generated by Django 5.0.4 on 2024-05-22 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_delivery_charge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_charge',
            field=models.CharField(max_length=100),
        ),
    ]
