# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-06 10:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_feedback'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitation',
            name='profile',
        ),
        migrations.AddField(
            model_name='invitation',
            name='profile',
            field=models.ManyToManyField(to='dashboard.Profile'),
        ),
    ]