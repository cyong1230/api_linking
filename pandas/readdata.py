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

Url_new = r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))"""
#ur'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'''
# the following two does not work well. 
#r"""((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)"""
#r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
AtMention = r'@[a-zA-Z0-9_]+'

url_regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

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
    html = re.sub(r'&#xA;&#xA;<pre.*?>.*?</pre>', '#CODE', html) # add .*? to match tag class
    html = re.sub(r'<pre.*?>.*?</pre>', '#CODE', html) # add this line to handle code snippet only posts. 
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

    pro = re.sub(Url_new, '#URL', pro, flags=re.DOTALL)
    pro = re.sub(AtMention, '@USER', pro)

    return pro

def replace_url_atmention(content):
    content = re.sub(AtMention, '@USER', content)
    content = re.sub(Url_new, '#URL', content, flags=re.DOTALL)
    return content

class DataReader:
    def __init__(self):
        self.db = MySQLdb.connect(host="localhost", user="root", passwd="ydh0114", db="stackoverflow201601")
        self.cur = self.db.cursor()
    
    def read_pandas_all(self):
        pandas_ids = []
        f = open('pandas_qid.txt', 'r')
        for line in f:
            pandas_ids.append(line.strip())
        f.close()
        fw = open('pandas_q_a_c.txt', 'w')
        cnt = 1
        for id in pandas_ids:
            print cnt
            try: 
                self.cur.execute("SELECT Title FROM posts where Id=%s" % (id))
                title = self.cur.fetchall()[0][0]
                fw.write(title + '\n')
                print "title finished... "
                self.cur.execute("SELECT Body FROM posts where Id=%s" %(id))
                qbody = self.cur.fetchall()[0][0]
                qbody = html2txt(qbody)
                fw.write(qbody + '\n')
                print "question body finished... "

                self.cur.execute("SELECT Text FROM comments where PostId=%s" % (id))
                qcomm = self.cur.fetchall()
                for qrow in qcomm:
                    tmp_qrow = html2txt(qrow[0])
                    fw.write(tmp_qrow + '\n')
                print "question comments finished... "

                self.cur.execute("SELECT Id FROM posts where ParentId=%s" %(id))
                aids = self.cur.fetchall()
                for row in aids:
                    aid = row[0]
                    self.cur.execute("SELECT Body FROM posts where Id=%s" %(aid))
                    abody = self.cur.fetchall()[0][0]
                    abody = html2txt(abody)
                    fw.write(abody + '\n')
                    
                    self.cur.execute("SELECT Text FROM comments where PostId=%s" % (aid))
                    acomm = self.cur.fetchall()
                    for arow in acomm:
                        tmp_arow = html2txt(arow[0])
                        fw.write(tmp_arow + '\n')
                print "answer and comments finished... "
            except:
                pass
            fw.write('\n')
            cnt += 1
        fw.close()

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

            # question comments
            self.cur.execute("SELECT Text FROM comments where PostId=%s" % (qid))
            qcomm = self.cur.fetchall()
            for qrow in qcomm: 
                f.write(qrow[0] + '\n')

            self.cur.execute("SELECT Id FROM posts where ParentId=%s" %(qid))
            aids = self.cur.fetchall()
            cnt = 1
            for row in aids:
                aid = row[0]
                self.cur.execute("SELECT Body FROM posts where Id=%s" %(aid))
                abody = self.cur.fetchall()[0][0]
                #f.write('\nA' + str(cnt) + ':\n' + html2txt(abody) + '\n')
                f.write(html2txt(abody) + '\n')
                # SO comments
                self.cur.execute("SELECT Text FROM comments where PostId=%s" % (aid))
                acomm = self.cur.fetchall()
                for arow in acomm: 
                    f.write(arow[0] + '\n')

                cnt += 1
        except:
            pass
        f.close()

if __name__ ==  '__main__':
    dr = DataReader()
    dr.read_pandas_all()
    #qids = [14262433,11346283,10715965,8991709,12555323,12065885,13148429,7837722,13413590,15891038]
    #qids = [14262433,11346283,10715965,8991709,12555323,12065885,13148429,7837722,15891038,13413590,
    #        12096252,11707586,19482970,13703720,15943769,13295735,18172851,16923281,20638006,16476924,
    #        12945971,19798153,14349055,10373660,25631076,17557074,10065051,13331698,11067027,12356501,
    #        11622652,20625582,11077023,17116814,11350770,10511024,10457584,13784192,17001389,14661701,
    #        18022845,10665889,13035764,12190874,14734533,14300137,18062135,13187778,19758364,11697887]
    #for qid in qids:
    #    dr.read(qid)
