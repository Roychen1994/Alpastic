# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-30 13:15
from __future__ import unicode_literals

import HdWxShop.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('HdWxShop', '0009_auto_20180704_2246'),
    ]

    operations = [
        migrations.CreateModel(
            name='useraddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UserAddress', models.CharField(max_length=255, null=True, verbose_name='地址')),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HdWxShop.webuser', verbose_name='用户名')),
            ],
        ),
        migrations.CreateModel(
            name='userwechat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=50)),
                ('unionid', models.CharField(max_length=100)),
                ('nickname', models.CharField(max_length=50)),
                ('sex', models.IntegerField()),
                ('province', models.CharField(blank=True, max_length=25, verbose_name='省份')),
                ('city', models.CharField(blank=True, max_length=25, verbose_name='地区')),
                ('country', models.CharField(blank=True, max_length=25, verbose_name='国家')),
                ('privilege', models.CharField(blank=True, max_length=255, verbose_name='用户特权信息')),
                ('userid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='HdWxShop.webuser')),
            ],
        ),
        migrations.AddField(
            model_name='newsinfo',
            name='Newsabstract',
            field=models.TextField(default=1, verbose_name='摘要'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='newsinfo',
            name='Newsimage',
            field=models.ImageField(blank=True, default='', null=True, upload_to=HdWxShop.models.upload_advimg, verbose_name='预览图片'),
        ),
        migrations.AddField(
            model_name='shoppingendflowproduct',
            name='Sefbrand',
            field=models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='品牌'),
        ),
        migrations.AddField(
            model_name='shoppingendflowproduct',
            name='seffunc',
            field=models.CharField(blank=True, default='', max_length=15, null=True, verbose_name='功能'),
        ),
        migrations.AlterField(
            model_name='userbind',
            name='Userwx',
            field=models.CharField(max_length=50, null=True, verbose_name='微信名'),
        ),
        migrations.AddIndex(
            model_name='useraddress',
            index=models.Index(fields=['userid'], name='HdWxShop_us_userid__051aaa_idx'),
        ),
    ]
