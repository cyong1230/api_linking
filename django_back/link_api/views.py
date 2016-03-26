from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict
from link_api.models import Record
import urlparse
import urllib
import subprocess
import re
import json
import os
import sys
from django.conf import settings
import texttoconll
import featureextractor
import nltk
import string
from multiprocessing import Pool

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from lxml import etree
import requests

token_list = []

def stem_tokens(tokens, stemmer):
	stemmed = []
	for item in tokens:
		stemmed.append(stemmer.stem(item))
	return stemmed

def tokenize(text):
	stemmer = PorterStemmer()
	tokens = nltk.word_tokenize(text)
	stems = stem_tokens(tokens, stemmer)
	return stems

def extract_txt(url):
	print url
	response = requests.get(url)
	parser = etree.HTMLParser()
	tree = etree.fromstring(response.text, parser)
	all_text = []

	for i in tree.xpath("//div[@class='body']"):
		text = etree.tostring(i, method='text', encoding='UTF-8')
		lowers = text.lower()
		all_text.append(lowers.translate(None, string.punctuation))

	return ' '.join(all_text)

def crawl(links, token_list):
	p = Pool()
	for idx, record in enumerate(links):
		p.apply_async(extract_txt, args=(record,), callback = log_result)			
	p.close()
	p.join()
	return token_list

def log_result(result):
	token_list.append(result)

@csrf_exempt
def extract_entity(request):
	print 'Begin POST'
	full_text = request.body
	with open(os.path.join(settings.STATIC_ROOT, 'demo.txt'), 'w') as demo_file:
		demo_file.write(full_text)

	texttoconll.main(os.path.join(settings.STATIC_ROOT, 'demo.txt'), os.path.join(settings.STATIC_ROOT, 'demo.conll'))
	featureextractor.main(os.path.join(settings.STATIC_ROOT, 'demo.conll'), os.path.join(settings.STATIC_ROOT, 'demo.data'))
	p = subprocess.Popen(['crf_test', '-m', os.path.join(settings.STATIC_ROOT, 'CRFmodel0'), os.path.join(settings.STATIC_ROOT, 'demo.data')], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	with open(os.path.join(settings.STATIC_ROOT, 'result.txt'), 'w') as demo_file:
		demo_file.write(out)
	arr = out.splitlines()
	# output = OrderedDict()
	output = []

	for idx, line in enumerate(arr):
		if not line.endswith("O") and line:
		# if line.endswith("B-API"):
			temp = re.sub('\t(.+)', ' ', line).strip()
			if (re.search('[a-zA-Z]+', temp)):
				output.append(temp)
	print output
	return HttpResponse(json.dumps(output))

@csrf_exempt
def link_entity(request):
	print 'Begin POST'
	body_unicode = request.body.decode('utf-8')
	# data = json.loads(body_unicode, object_pairs_hook=OrderedDict)
	data = json.loads(body_unicode, object_pairs_hook=OrderedDict)
	data_entity = data["entity"]
	question_title = data["title"].strip().lower()
	tag_list = [x.lower() for x in data["tags"]]
	href_list = [x.lower() for x in data["hrefs"]]
	encode_texts = data["texts"].encode('ascii', errors='xmlcharrefreplace')
	full_text = encode_texts.translate(None, string.punctuation)

	href_info = [];
	result_list = [];
	
	for href in href_list:
		temp = {}
		o = urlparse.urlsplit(href.encode('ascii','ignore').strip().lower())
		temp['domain'] = o.netloc
		temp['file'] = o.path.rsplit('/', 1)[-1]
		href_info.append(temp)

	for key in data_entity:
		value = data_entity[key]
		try:
			record_list = Record.objects.filter(name=value)
		except Record.DoesNotExist:
			continue
		else:
			if record_list.count() == 0:
				result = []
				result_list.append(result)
			elif record_list.count() == 1:
				record = record_list[0]
				result = [{}]
				result[0]['name'] = value
				result[0]['url'] = record.url
				result[0]['lib'] = record.lib
				result_list.append(result)
			else:
				result_sublist = [];
				# tf-idf
				links = [];
				for record in record_list:
					links.append(urlparse.urlsplit(record.url.encode('ascii','ignore').strip()).geturl())

				del token_list[:]

				token_list.append(full_text);
				crawl(links, token_list)

				tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
				tfs = tfidf.fit_transform(token_list)
				tdidf_result = (tfs * tfs.T).A[0]

				# url, tag, title
				for idx, record in enumerate(record_list):
					mark = [False] * 3
					result = {};

					a = record.url.lower()
					r = urlparse.urlsplit(a.encode('ascii','ignore').strip())

					for link in href_info:
						if(link['domain'] == r.netloc and link['file'] == r.path.rsplit('/', 1)[-1]):
							mark[0] = True;

					if record.lib in tag_list:
						mark[1] = True;
					
					if record.lib in question_title:
						mark[2] = True;

					result['mark'] = mark
					result['score'] = sum(b<<i for i, b in enumerate(mark))
					result['name'] = value
					result['url'] = record.url
					result['lib'] = record.lib
					result['tfidf'] = tdidf_result[idx+1]
					result_sublist.append(result)

				result_list.append(result_sublist)
	# print result_list
	return HttpResponse(json.dumps(result_list))