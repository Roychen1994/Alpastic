# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-04 14:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HdWxShop', '0008_auto_20180704_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commditydetail',
            name='Codbrand',
            field=models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='品牌'),
        ),
        migrations.AlterField(
            model_name='commditydetail',
            name='Codfunction',
            field=models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='功能'),
        ),
    ]
