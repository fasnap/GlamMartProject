# Generated by Django 5.0.4 on 2024-05-31 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_returnrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Ordered', 'Ordered'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned')], default='New', max_length=10),
        ),
    ]
