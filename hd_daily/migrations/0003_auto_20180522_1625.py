# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-22 08:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hd_daily', '0002_auto_20180522_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='date_done',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
