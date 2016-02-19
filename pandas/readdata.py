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

mycompile = lambda pat:  re.compile(pat,  re.UNICODE)
WS_RE = mycompile(r'  +')

def squeeze_whitespace(s):
    new_string = WS_RE.sub(" ",s)
    return new_string.strip()

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    f.close()
    return i 

def my_encoder(my_string):
    for i in my_string:
        try:
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
    html = re.sub(r'<code>', '`', html)
    html = re.sub(r'</code>', '`', html)
    html = re.sub(r'<pre>.*?</pre>', '@CODE', html)
    #html = re.sub(r'(`(?=\S)|(?<=\S)`)', '', html)
    html = re.sub(r'(&#xA;)+','\n', html)
    s.feed(html)
    return s.get_data()

def html2txt(content):
    pro = ''.join( my_encoder( strip_tags(content) ) )
    pro = re.sub(r'^ +', '', pro)
    pro = re.sub(r'\n +', '\n', pro)
    pro = re.sub(r'[\n]+', '\n',pro)
    pro = squeeze_whitespace(pro)
    return pro

class DataReader:
    def __init__(self):
        self.db = MySQLdb.connect(host="localhost", user="root", passwd="ydh0114", db="stackoverflow201508")
        self.cur = self.db.cursor()

    def read(self, qid):
        f = open('./sodata/' + str(qid) + '.txt', 'w')
        try:
            self.cur.execute("SELECT Title FROM posts where Id=%s" % (qid))
            title = self.cur.fetchall()[0][0]
			#f.write('Title:\n' + title + '\n')
            f.write(title + '\n')

            self.cur.execute("SELECT Body FROM posts where Id=%s" %(qid))
            qbody = self.cur.fetchall()[0][0]
            #f.write('\nQ:\n' + html2txt(qbody) + '\n')
            f.write(html2txt(qbody) + '\n')

            self.cur.execute("SELECT Id FROM posts where ParentId=%s" %(qid))
            aids = self.cur.fetchall()
            cnt = 1
            for row in aids:
                aid = row[0]
                self.cur.execute("SELECT Body FROM posts where Id=%s" %(aid))
                abody = self.cur.fetchall()[0][0]
                #f.write('\nA' + str(cnt) + ':\n' + html2txt(abody) + '\n')
                f.write(html2txt(abody) + '\n')
                cnt += 1
        except:
            pass
        f.close()

if __name__ ==  '__main__':
    dr = DataReader()
	#qids = [5486226, 5515021, 5558607,5955695,6467832,7577546,7776679,7813132,7837722,8273092]
	#qids = [14262433,11346283,10715965,8991709,12555323,12065885,13148429,7837722,13413590,15891038]
    qids = [14262433,11346283,10715965,8991709,12555323,12065885,13148429,7837722,15891038,13413590,
            12096252,11707586,19482970,13703720,15943769,13295735,18172851,16923281,20638006,16476924,
            12945971,19798153,14349055,10373660,25631076,17557074,10065051,13331698,11067027,12356501,
            11622652,20625582,11077023,17116814,11350770,10511024,10457584,13784192,17001389,14661701,
            18022845,10665889,13035764,12190874,14734533,14300137,18062135,13187778,19758364,11697887]
    for qid in qids:
        dr.read(qid)