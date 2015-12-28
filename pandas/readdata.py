# -*- coding: utf-8 -*-

import sys,os
import MySQLdb
import re
from HTMLParser import HTMLParser
from htmlentitydefs import entitydefs
from random import randint
import codecs

codecs.register_error('replace_against_space', lambda e: (u' ',e.start + 1))
#print unicode('ABC\x97ab\x99c上午', 'utf-8', errors='replace_against_space')

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    f.close()
    return i 

def my_encoder(my_string):
   for i in my_string:
      try :
         yield unicode(i, 'utf-8')
      except UnicodeDecodeError:
         yield ' ' # or another whitespaces 

def strip_backtick(istring):
    return re.sub(r'(`(?=\S)|(?<=\S)`)', '', istring)  # this is hacky. Deheng

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
        self.entityref = re.compile('&[a-zA-Z][-.a-zA-Z0-9]*[^a-zA-Z0-9]')
    
    def handle_data(self, d):
        self.fed.append(d)

    def handle_starttag(self, tag, attrs):
        self.fed.append(' ')

    def handle_endtag(self, tag):
        self.fed.append(' ')
   
    def handle_entityref(self, name):
        if entitydefs.get(name) is None:
            m = self.entityref.match(self.rawdata.splitlines()[self.lineno-1][self.offset:])
            entity = m.group()
            # semicolon is consumed, other chars are not.
            if entity is not None:
            	#print "entity is none"
            	if entity[-1] != ';':
                	entity = entity[:-1]
            	self.fed.append(entity)
            else: 
            	self.fed.append('')
        else:
            self.fed.append(' ')

    def get_data(self):
        self.close()
        return ''.join(self.fed) 

def strip_tags(html):
    s = MLStripper()
    html = re.sub(r'&#xA;&#xA;<pre>.*?</pre>', '@codeSnippetRemoved', html)
    html = re.sub(r'(`(?=\S)|(?<=\S)`)', '', html)
    html = re.sub(r'(&#xA;&#xA;)+','\n', html)
    s.feed(html)
    return s.get_data()


class DataReader:
	def __init__(self):
		self.db = MySQLdb.connect(host="localhost", 
		                     user="root", 
		                     passwd="ydh0114", 
		                     db="stackoverflow201508")
		self.cur = self.db.cursor() 

	def read(self, qid):
		try:
			f = open('./sodata/' + str(qid) + '.txt', 'w')

			self.cur.execute("SELECT Title FROM posts where Id=%s" % (qid))
			title = self.cur.fetchall()[0][0]
			f.write('Title:\n' + title + '\n')

			self.cur.execute("SELECT Body FROM posts where Id=%s" %(qid))
			qbody = self.cur.fetchall()[0][0]
			f.write('Q:\n' + qbody + '\n')
			
			self.cur.execute("SELECT Id FROM posts where ParentId=%s" %(qid))
			aids = self.cur.fetchall()
			cnt = 1
			for row in aids:
				aid = row[0]
				self.cur.execute("SELECT Body FROM posts where Id=%s" %(aid))
				abody = self.cur.fetchall()[0][0]
				f.write('A' + str(cnt) + ':\n' + abody + '\n')
				cnt += 1

			f.close()
			
			# f = open('./sodata/' + str(qid) + '.txt', 'w')

			# for row in all:
			# 	content = ''.join( my_encoder( strip_tags(row[0]) ) )
			# 	content = re.sub(r'^ +', '', content)
			# 	content = re.sub(r'\n +', '\n', content)
			# 	content = re.sub(r'[\n]+', '\n',content)

			# 	f.write(content +'\n')
			# f.close()
		except:
			pass

if __name__ ==  '__main__':
	dr = DataReader()
	dr.read(11346283)