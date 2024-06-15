# Generated by Django 5.0.4 on 2024-05-24 11:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0003_coupon_min_purchase_amount'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupons',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('discount', models.CharField(max_length=3)),
                ('status', models.BooleanField(default=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('valid_to', models.DateField()),
                ('valid_from', models.DateField()),
            ],
        ),
        migrations.RemoveField(
            model_name='usercoupon',
            name='coupon',
        ),
        migrations.RemoveField(
            model_name='usercoupon',
            name='user',
        ),
        migrations.CreateModel(
            name='CouponCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coupons.coupons')),
            ],
        ),
        migrations.DeleteModel(
            name='Coupon',
        ),
        migrations.DeleteModel(
            name='UserCoupon',
        ),
    ]
