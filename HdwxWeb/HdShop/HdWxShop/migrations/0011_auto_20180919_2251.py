# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-19 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HdWxShop', '0010_auto_20180830_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingflow',
            name='sfpayname',
            field=models.CharField(blank=True, max_length=100, verbose_name='财务人员'),
        ),
        migrations.AlterField(
            model_name='shoppingflow',
            name='sfpaytime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='付款时间'),
        ),
        migrations.AlterField(
            model_name='shoppingflow',
            name='sfsmname',
            field=models.CharField(blank=True, max_length=100, verbose_name='出货人员'),
        ),
        migrations.AlterField(
            model_name='shoppingflow',
            name='sfsmtime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='出货时间'),
        ),
        migrations.AlterField(
            model_name='shoppingflow',
            name='sfsubmitname',
            field=models.CharField(blank=True, max_length=100, verbose_name='确认人员'),
        ),
        migrations.AlterField(
            model_name='shoppingflow',
            name='sfsubmittime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='确认时间'),
        ),
    ]
