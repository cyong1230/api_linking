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
import twokenize
import texttoconll
import featureextractor
import nltk
import string
from multiprocessing import Pool
import string
import collections

from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from lxml import etree
import requests

token_list = {}

def stem_tokens(tokens, stemmer):
	stemmed = []
	for item in tokens:
		stemmed.append(stemmer.stem(item))
	return stemmed

def lemma_tokens(tokens, lmtzr):
	lemmatized = []
	for item in tokens:
		lemmatized.append(lmtzr.lemmatize(item))
	return lemmatized

def tokenize(text):
	stemmer = PorterStemmer()
	# lmtzr = WordNetLemmatizer()
	tokens = twokenize.tokenize(text)
	tokens_clean = [s for s in tokens if s not in set(string.punctuation)]
	# tokens = nltk.word_tokenize(text)
	stems = stem_tokens(tokens_clean, stemmer)
	# lemmas = lemma_tokens(tokens, lmtzr)
	return stems

def extract_txt(url,idx):
	print url
	response = requests.get(url)
	parser = etree.HTMLParser()
	tree = etree.fromstring(response.text, parser)
	all_text = []

	for i in tree.xpath("//div[@class='body']"):
		text = etree.tostring(i, method='text', encoding='UTF-8')
		# lowers = text.lower()
		all_text.append(text)

	return (idx+1, ' '.join(all_text))

def crawl(links, token_list):
	p = Pool()
	for idx, record in enumerate(links):
		p.apply_async(extract_txt, args=(record,idx), callback = log_result)			
	p.close()
	p.join()
	return token_list

def log_result(result):
	token_list[result[0]] = result[1]

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
	# print output
	return HttpResponse(json.dumps(output))

@csrf_exempt
def link_entity(request):
	print 'Begin POST'
	body_unicode = request.body.decode('utf-8')
	# data = json.loads(body_unicode, object_pairs_hook=OrderedDict)
	data = json.loads(body_unicode, object_pairs_hook=OrderedDict)
	data_entity = data["entityList"]
	data_entity_index = data["entityIndex"]
	question_title = re.findall(r"[\w']+", data["title"].lower())
	tag_list = [x.lower() for x in data["tags"]]
	href_list = [x.lower() for x in data["hrefs"]]
	encode_texts = data["texts"].encode('ascii', errors='xmlcharrefreplace')
	full_text = encode_texts.translate(None, string.punctuation)

	href_info = [];
	result_list = [];
	class_list = [];
	
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
				continue
			elif record_list.count() == 1:
				record = record_list[0]
				if record.api_type == "class":
					class_list.append((value, data_entity_index[int(key)]))
			else:
				result_sublist = [];

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

					result['score'] = sum(b<<i for i, b in enumerate(mark))
					result['name'] = value
					result['type'] = record.api_class
					result_sublist.append(result)
				maxScoreResult = max(result_sublist, key=lambda x:x['score'])
				if maxScoreResult['type'] == 'class':
					class_list.append((maxScoreResult['name'], data_entity_index[int(key)]))
	print class_list

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
				result[0]['type'] = record.api_type
				result[0]['url'] = record.url
				result[0]['lib'] = record.lib
				result_list.append(result)
			else:
				result_sublist = [];

				####### tf-idf ##########
				links = []
				tdidf_result = []
				for record in record_list:
					links.append(urlparse.urlsplit(record.url.encode('ascii','ignore').strip()).geturl())

				token_list.clear()
				token_list_sorted = []

				token_list[0] = full_text;
				crawl(links, token_list)
				token_od = collections.OrderedDict(sorted(token_list.items()))

				for item in token_od.itervalues():
					token_list_sorted.append(item)

				# gensim
				# dictionary = corpora.Dictionary(token_list)
				# corpus = [dictionary.doc2bow(text) for text in token_list]
				# tfidf = models.TfidfModel(corpus)
				# index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary))
				# tdidf_result = index[tfidf[corpus[0]]]

				# sklearn
				tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
				tfs = tfidf.fit_transform(token_list_sorted)
				tdidf_result = (tfs * tfs.T).A[0]

				######### url, tag, title ############
				for idx, record in enumerate(record_list):
					mark = [False] * 4
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

					for valid_class in class_list:
						# if Levenshtein.ratio(valid_class, record.api_class) > 0.9:
						if valid_class[0] in record.api_class:
							mark[3] = True
							result['distance'] = abs(int(key) - valid_class[1])
						else:
							result['distance'] = -1

					result['mark'] = mark
					result['score'] = sum(b<<i for i, b in enumerate(mark))
					result['name'] = value
					result['url'] = record.url
					result['lib'] = record.lib
					result['type'] = record.api_type
					result['tfidf'] = str(tdidf_result[idx+1])
					result_sublist.append(result)
				minDistanceResult = min((x for x in result_sublist if x['distance'] >= 0), key=lambda x:x['distance'])
				for key, result in enumerate(result_sublist):
					if(result['url'] == minDistanceResult['url']):
						result['score'] = result['score'] + 1
				result_list.append(result_sublist)

	# print result_list
	return HttpResponse(json.dumps(result_list))