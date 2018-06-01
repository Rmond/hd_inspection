# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=32,primary_key=True,unique=True)
    nickname = models.CharField(max_length=16)
    password = models.CharField(max_length=128)
    role = models.PositiveSmallIntegerField(default=1)
    USERNAME_FIELD = 'username'

class Inspection(models.Model):
    Stats = (
         (0, u'正常'),
         (1, u'故障'),
    )
    date_done = models.CharField(primary_key=True,max_length=10)
    username = models.CharField(max_length=32)
    server_stats = models.PositiveSmallIntegerField(choices=Stats)
    backup_stats = models.PositiveSmallIntegerField(choices=Stats)
    remark = models.TextField(default="")