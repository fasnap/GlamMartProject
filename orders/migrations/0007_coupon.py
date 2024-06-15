# Generated by Django 5.0.4 on 2024-05-23 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_order_delivery_charge_alter_order_order_total_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('discount', models.IntegerField(default=1)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
