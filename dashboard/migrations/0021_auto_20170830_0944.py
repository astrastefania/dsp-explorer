# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-30 09:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0020_auto_20170830_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='source_of_innovation',
            field=models.ManyToManyField(related_name='profilesourceofinnovation', to='dashboard.SourceOfInnovation'),
        ),
    ]
