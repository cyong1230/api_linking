from __future__ import unicode_literals

from django.db import models

class Record(models.Model):
	name = models.CharField(max_length=200, primary_key=True)
	url = models.URLField()
