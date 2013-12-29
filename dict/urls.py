# coding=UTF-8

from django.conf.urls import patterns, url

from dict import views

urlpatterns = patterns('',
        # ex: /dict/
        url(r'^$', views.index, name='index'),
        # ex: /dict/weblios/hello/?callback=xxx
        url(r'^(?P<dict_type>weblio|weblio_small|wiktionary|wiki_jp|ewords)/(?P<key>[^\/]+)/$', views.query, name='query'),

)
