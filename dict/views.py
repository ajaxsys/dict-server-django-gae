import urllib2
import re
import logging
import conf

import json

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404

#from django.template import RequestContext, loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from dict.models import Weblio,Weblio_Small,Wiktionary,Ewords,Wiki_JP



logger = logging.getLogger('dict')
#If read/write to DB
DB_MODE = True


def index(request):
    context = {}
    return render(request, 'dict/index.html', context)

def query(request, dict_type, key):
    key = cleanKey(key)

    word = getWordFromDB(dict_type, key)
    if word is not None:
        #print "db"
        logger.info( "Read key `%s` from local DB: %s", key, dict_type )
    else:
        # Get from internet
        word = fetchURL(dict_type, key)
        if word is not None :
            saveWordToDB(dict_type, word)
        else:
            #raise Http404
            word = {'word': key,'explain': 'Not found', 'reference':'local&internet'}
        # change dict to object http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
        word=Struct(**word)

    callback = request.GET.get('callback')
    if callback is None or not callback.startswith('DICT'):
        # Html style response
        context = { 
            'dict_type': dict_type, 
            'dict' : word
        }
        return render(request, 'dict/query.html', context)
    else:
        #JSON style response
        context = {
            'type': dict_type, 
            'src' : word.explain,
            'word' : word.word,
            'ref': word.reference
        }
        return HttpResponse(callback+'('+json.dumps(context)+')', mimetype="application/javascript; charset=utf-8")

#########################
# Private functions
#########################
class Struct:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

def cleanKey(key):
    newKey = key.lower().strip()
    if key != newKey:
        logger.info("Change key FROM %s TO %s", key, newKey)

    return key.lower().strip()


def fetchURL(dict_type, key):
    logger.info( "Fetch %s from internet. (%s)", key, dict_type)

    #fetchUrls = FetchURL.objects.filter(dict_name=dict_type).order_by('-level')
    fetchUrls = conf.fetch_urls(dict_type)
    if fetchUrls is None :
        return None
    #`q=` is called `relative quality factor`.
    hdr = {
        'User-Agent': '',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'utf-8,shift-JIS;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'ja,en-us,*;q=0.3',
        'Connection': 'keep-alive'
    }

    # decode: string --> unicode
    # encode: string <-- unicode
    fetchKey = urllib2.quote(key.encode('utf8'))
    for fetchUrl in fetchUrls:
        # Change UA
        hdr['User-Agent']=fetchUrl['ua']
        # Get URL
        url = fetchUrl['fetch_url'].replace('#key#',fetchKey)
        logger.info( "Fetching url: %s " , url )
        req = urllib2.Request(url, headers=hdr)

        try:
            response = urllib2.urlopen(req)
            html = response.read()
            # whatisthis(html) # ordinary string
            logger.debug( "html: \n" + html )
            if html is not None:
                return {
                    'word': key,
                    #'explain': toJSStr(html),
                    #'explain': unicode(html,errors='ignore'), #unicode only
                    # TODO: decode by <meta charset>
                    'explain': html.decode('utf-8',errors='ignore'),
                    'reference': url
                }
        except urllib2.HTTPError, e:
            logger.error("********ERROR******** \n" + e.fp.read() + "\n********ERROR********")
            continue
        except (Http404):
            logger.error("HTTP ERROR 404")
            continue
    return None

def getWordFromDB(dict_type,key) :
    if not DB_MODE : 
        return None
    try:
        if isTable(dict_type, Weblio) :
            #word = get_object_or_404(Weblio, word=key)
            return Weblio.objects.get(word=key) #filter(word=key)[0]
        elif isTable(dict_type, Weblio_Small) :
            #word = get_object_or_404(Weblio, word=key)
            return Weblio_Small.objects.get(word=key)
        elif isTable(dict_type, Ewords) :
            #word = get_object_or_404(Ewords, word=key)
            return Ewords.objects.get(word=key)
        elif isTable(dict_type, Wiktionary) :
            #word = get_object_or_404(Ewords, word=key)
            return Wiktionary.objects.get(word=key)
        elif isTable(dict_type, Wiki_JP) :
            #word = get_object_or_404(Ewords, word=key)
            return Wiki_JP.objects.get(word=key)
        else:
            #print "Ingnore getWordFromDB" + dict_type
            logger.warn("Ingnore getWordFromDB" + dict_type)
            return None
    except (Weblio.DoesNotExist, Weblio_Small.DoesNotExist, Ewords.DoesNotExist, Wiktionary.DoesNotExist, Wiki_JP.DoesNotExist):
        return None


def saveWordToDB(dict_type, record):
    if not DB_MODE : 
        return None
    # record is dictionary in python
    #print "Save to DB:" + dict_type + ". word:" + record['word']
    logger.info("Save to DB:" + dict_type + ". word:" + record['word'])

    # print ". explian: " + record.get('explain')
    # print "Refer:" + record.get('reference')

    if isTable(dict_type, Weblio) :
        obj = Weblio(word=record['word'], explain=record['explain'], reference=record['reference'])
    elif isTable(dict_type, Weblio_Small) :
        obj = Weblio_Small(word=record['word'], explain=record['explain'], reference=record['reference'])
    elif isTable(dict_type, Ewords) :
        obj = Ewords(word=record['word'], explain=record['explain'], reference=record['reference'])
    elif isTable(dict_type, Wiktionary) :
        obj = Wiktionary(word=record['word'], explain=record['explain'], reference=record['reference'])
    elif isTable(dict_type, Wiki_JP) :
        obj = Wiki_JP(word=record['word'], explain=record['explain'], reference=record['reference'])
    else: 
        #print "Ingnore saveWordToDB" + dict_type
        logger.warn("Ingnore saveWordToDB" + dict_type) 
        return None
    obj.save()

def isTable(table_name, clazz):
    return table_name.lower() == clazz.__name__.lower()

def toJSStr(str) :
    str = re.sub(r'\\','\\\\',str)
    str = re.sub(r'\n','\\n',str)
    str = re.sub(r'"','\\"',str)
    str = re.sub(r'\t','\\t',str)
    return str

def whatisthis(s):
    if isinstance(s, str):
        print "ordinary string"
    elif isinstance(s, unicode):
        print "unicode string"
    else:
        print "not a string"


