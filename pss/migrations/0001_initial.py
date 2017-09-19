# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-03 15:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dashboard', '0014_auto_20170718_1044'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('les', models.IntegerField(choices=[(0, 'Lama'), (1, 'Topix'), (2, 'NoIdea')], default=0)),
                ('project_name', models.TextField(max_length=500, verbose_name='Project Name')),
                ('zip_location', models.FileField(upload_to='application', verbose_name='Zip Location')),
                ('created_at', models.DateTimeField(blank=True, default=datetime.datetime.now, null=True)),
                ('profile', models.ManyToManyField(to='dashboard.Profile')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
    ]
