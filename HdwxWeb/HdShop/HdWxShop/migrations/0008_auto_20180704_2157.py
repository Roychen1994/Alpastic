# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-04 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HdWxShop', '0007_auto_20180604_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='commditydetail',
            name='Codbrand',
            field=models.CharField(default='', max_length=15, verbose_name='品牌'),
        ),
        migrations.AddField(
            model_name='commditydetail',
            name='Codfunction',
            field=models.CharField(default='', max_length=15, verbose_name='功能'),
        ),
    ]