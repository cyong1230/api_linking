from __future__ import unicode_literals

from django.db import models

class Record(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=200)
	url = models.URLField()
	lib = models.CharField(max_length=200)
	
	def __str__(self):
		return self.name