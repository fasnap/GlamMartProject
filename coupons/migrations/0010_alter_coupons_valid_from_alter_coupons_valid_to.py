# Generated by Django 5.0.4 on 2024-06-03 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0009_coupons_coupon_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupons',
            name='valid_from',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='coupons',
            name='valid_to',
            field=models.DateTimeField(),
        ),
    ]
