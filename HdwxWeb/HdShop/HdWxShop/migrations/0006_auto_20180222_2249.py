# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-22 14:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HdWxShop', '0005_auto_20180220_2200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commditydetail',
            name='CodSpec',
        ),
        migrations.AddField(
            model_name='commditydetail',
            name='CodSize',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='尺寸'),
        ),
        migrations.AddField(
            model_name='commditydetail',
            name='Cod_Protlevel',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='环保等级'),
        ),
        migrations.AddField(
            model_name='commditydetail',
            name='Codthick',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='厚度'),
        ),
    ]
