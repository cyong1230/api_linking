# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-17 16:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('link_api', '0004_webcache'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webcache',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
