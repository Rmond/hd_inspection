#!/usr/local/bin/python2.7
# encoding: utf-8

from django.conf.urls import url

import views


urlpatterns = [
    url(r'^$',views.login),
    url(r'^login',views.login),
    url(r'^index',views.index),
    url(r'^logout$',views.logout),
    url(r'^userlist',views.user_list),
    url(r'^useradd',views.user_add),
    url(r'^pwdreset',views.pwd_reset),
    url(r'^userdel',views.user_del),
    url(r'^userlook',views.user_look),
    url(r'^userinfo',views.user_info),
    url(r'^useredit',views.user_edit),
    url(r'^usernamechk',views.username_check),
    url(r'^dailylist',views.daily_list),
    url(r'^dailyadd',views.daily_add),
]
