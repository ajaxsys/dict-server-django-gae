UA_IOS_5='Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
UA_IOS_6='Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25'

weblio_sp = {
    'fetch_url' : 'http://ejje.weblio.jp/content/#key#',
    'ua' : UA_IOS_6,
}
weblio_small = {
    'fetch_url' : 'http://ejje.weblio.jp/small/content/#key#',
    'ua' : UA_IOS_6,
}

ewords = {
    'fetch_url' : 'http://e-words.jp/w/#key#.html',
    'ua' : UA_IOS_6,
}
wiki_jp = {
    #'fetch_url' : 'http://ja.wikipedia.org/wiki/#key#',
    'fetch_url' : 'http://ja.wikipedia.org/w/index.php?search=#key#',
    'ua' : UA_IOS_6,
}


# Rules for fetching URLs
fetch_rules = {
    #deprecated
    'weblio_small':[
        weblio_small
    ],
    'weblio':[
        weblio_sp
    ],
    'wiki_jp': [wiki_jp],
}

def fetch_urls(dict_name):
    return fetch_rules.get(dict_name, None)

