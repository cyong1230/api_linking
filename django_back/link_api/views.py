from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict
from link_api.models import Record

import json

@csrf_exempt
def get_url(request):
	print 'Begin POST'
	data = json.loads(request.body, object_pairs_hook=OrderedDict)
	result = {};

	for key in data:
		value = data[key]
		try:
			record = Record.objects.get(name=value)
		except Record.DoesNotExist:
			continue
		else:
			result[key] = {}
			result[key]['name'] = value
			result[key]['url'] = record.url

	return HttpResponse(json.dumps(result))