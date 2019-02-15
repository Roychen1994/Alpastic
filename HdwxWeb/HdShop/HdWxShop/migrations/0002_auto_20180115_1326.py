# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-15 05:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('HdWxShop', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commodityclass',
            options={'verbose_name': '商品类别', 'verbose_name_plural': '商品类别'},
        ),
        migrations.AlterModelOptions(
            name='commodityinfo',
            options={'verbose_name': '商品信息', 'verbose_name_plural': '商品信息'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'verbose_name': '购物车', 'verbose_name_plural': '购物车'},
        ),
        migrations.AlterModelOptions(
            name='userrole',
            options={'verbose_name': '角色权限', 'verbose_name_plural': '角色权限'},
        ),
        migrations.AlterModelOptions(
            name='userrule',
            options={'verbose_name': '用户权限', 'verbose_name_plural': '用户权限'},
        ),
        migrations.AlterModelOptions(
            name='webuser',
            options={'verbose_name': '用户信息', 'verbose_name_plural': '用户信息'},
        ),
        migrations.AlterField(
            model_name='advinfo',
            name='Advcommid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HdWxShop.commodityinfo'),
        ),
        migrations.AlterField(
            model_name='commditydetail',
            name='CodSpec',
            field=models.CharField(max_length=50, null=True, verbose_name='规格'),
        ),
        migrations.AlterField(
            model_name='commditydetail',
            name='CodUnit',
            field=models.CharField(max_length=50, null=True, verbose_name='单位'),
        ),
        migrations.AlterField(
            model_name='commditydetail',
            name='CodunPrice',
            field=models.FloatField(verbose_name='单价'),
        ),
        migrations.AlterField(
            model_name='commodityclass',
            name='CclassName',
            field=models.CharField(max_length=50, unique=True, verbose_name='商品类别'),
        ),
        migrations.AlterField(
            model_name='commodityinfo',
            name='CommInfo',
            field=models.ImageField(upload_to='HdShop/CommdityFile'),
        ),
        migrations.AlterField(
            model_name='commodityinfo',
            name='CommName',
            field=models.CharField(max_length=100, unique=True, verbose_name='商品名称'),
        ),
        migrations.AlterField(
            model_name='custcommprice',
            name='Cpcommid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HdWxShop.commditydetail', verbose_name='商品及规格'),
        ),
        migrations.AlterField(
            model_name='custcommprice',
            name='CpunPrice',
            field=models.FloatField(verbose_name='单价'),
        ),
        migrations.AlterField(
            model_name='custcommprice',
            name='Cpuserid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HdWxShop.webuser', verbose_name='用户名'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='ScCollectid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HdWxShop.commditydetail'),
        ),
        migrations.AlterField(
            model_name='shoppingflow',
            name='Scid',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='HdWxShop.shoppingcart'),
        ),
        migrations.AlterField(
            model_name='shoppingflow',
            name='Sfstatus',
            field=models.IntegerField(choices=[(1, '有意向'), (2, '生成已订单'), (3, '价格待审核'), (4, '客户待确认'), (5, '待付款'), (6, '待出货'), (7, '待收货')]),
        ),
        migrations.AlterField(
            model_name='userbind',
            name='UserAddress',
            field=models.CharField(max_length=255, null=True, verbose_name='地址'),
        ),
        migrations.AlterField(
            model_name='userbind',
            name='Userphone',
            field=models.CharField(max_length=30, null=True, verbose_name='手机号码'),
        ),
        migrations.AlterField(
            model_name='userbind',
            name='Userwx',
            field=models.CharField(max_length=50, null=True, verbose_name='微信号'),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='Username',
            field=models.CharField(max_length=100, unique=True, verbose_name='用户名'),
        ),
        migrations.AlterField(
            model_name='webuser',
            name='Userstatus',
            field=models.IntegerField(choices=[(0, '异常'), (1, '正常'), (2, '冻结')], default=1, verbose_name='状态'),
        ),
    ]