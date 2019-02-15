# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-17 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HdWxShop', '0004_auto_20180416_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingendflow',
            name='sefpayname',
            field=models.CharField(default=-1, max_length=100, verbose_name='财务人员'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shoppingendflow',
            name='sefpaytime',
            field=models.DateTimeField(null=True, verbose_name='付款时间'),
        ),
        migrations.AddField(
            model_name='shoppingendflow',
            name='sefsmname',
            field=models.CharField(default=-1, max_length=100, verbose_name='出货人员'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shoppingendflow',
            name='sefsmtime',
            field=models.DateTimeField(null=True, verbose_name='出货时间'),
        ),
        migrations.AddField(
            model_name='shoppingendflow',
            name='sefsubmitname',
            field=models.CharField(default=-1, max_length=100, verbose_name='管理人员'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shoppingendflow',
            name='sefsubmittime',
            field=models.DateTimeField(null=True, verbose_name='确认时间'),
        ),
        migrations.AddField(
            model_name='shoppingflow',
            name='sfpayname',
            field=models.CharField(default=-1, max_length=100, verbose_name='财务人员'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shoppingflow',
            name='sfpaytime',
            field=models.DateTimeField(null=True, verbose_name='付款时间'),
        ),
        migrations.AddField(
            model_name='shoppingflow',
            name='sfsmname',
            field=models.CharField(default=-1, max_length=100, verbose_name='出货人员'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shoppingflow',
            name='sfsmtime',
            field=models.DateTimeField(null=True, verbose_name='出货时间'),
        ),
        migrations.AddField(
            model_name='shoppingflow',
            name='sfsubmitname',
            field=models.CharField(default=-1, max_length=100, verbose_name='管理人员'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shoppingflow',
            name='sfsubmittime',
            field=models.DateTimeField(null=True, verbose_name='确认时间'),
        ),
    ]
