# Generated by Django 5.0.4 on 2024-06-03 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0010_alter_coupons_valid_from_alter_coupons_valid_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupons',
            name='valid_from',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='coupons',
            name='valid_to',
            field=models.DateField(),
        ),
    ]
