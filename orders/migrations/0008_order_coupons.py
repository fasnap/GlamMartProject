# Generated by Django 5.0.4 on 2024-05-24 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupons',
            field=models.ManyToManyField(blank=True, to='orders.coupon'),
        ),
    ]
