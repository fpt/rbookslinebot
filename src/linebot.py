#!/usr/bin/env python
# coding:utf-8

import pprint
import requests
from argparse import ArgumentParser
import sys, os
import MeCab
import logging
#from gensim.models.word2vec import Word2Vec
from bookswscli import BooksCategory, BooksWSClient
import configparser

logging.basicConfig(level=logging.DEBUG)


def main():
    parser = ArgumentParser()
    parser.add_argument('query', nargs='?', help='query string')
    args = parser.parse_args()

    qstr = args.query
    #doProcessMessage(qstr)

    conf = BooksBotConfig()

    bot = BooksLineBot(conf)
    bot.processMessageText(u'安い本')
    bot.processMessageText(u'名探偵コナン')
    bot.processMessageText(u'絵本')
    bot.processMessageText(u'きゃりーぱみゅぱみゅ')
    rs = bot.processMessageText(u'おすすめのDVD')
    rc = bot.makeResultMsg(rs)
    logging.debug(rc)


class BooksBotConfig():
    def __init__(self):
        here = os.path.dirname(__file__)
        inifile = os.path.join(here, r'../config.ini')
        config = configparser.ConfigParser()
        config.read(inifile)
        assert 'line' in config and 'rakuten' in config
        self.config = config

    def getLineBotToken(self):
        return self.config['line']['bottoken']

    def getRakutenAppID(self):
        return self.config['rakuten']['appid']


class BooksLineBot():
    def __init__(self, conf):
        self.conf = conf

        self.m = MeCab.Tagger()
        self.cat = BooksCategory()
        self.cat.load()
        self.bkc = BooksWSClient(conf.getRakutenAppID())

    def processMessage(self, json):
        ev      = json['events'][0]
        token   = ev['replyToken']
        typ     = ev['type']
        source  = ev['source']
        message = ev['message']
        txt     = message['text']

        logging.info(token)
        logging.info(typ)
        logging.info(source)
        logging.info(message)
        logging.info(txt)

        respmsgs = None
        if txt.lower() in ['hi', 'yo', 'gm', 'gn', u'はろ', u'こん', u'おっす', u'おやす']:
            # o-mugaeshi
            respmsgs = [{'type' : 'text', 'text' : txt}]
        else:
            rs = self.processMessageText(txt)
            if not rs:
                respmsgs = [{'type' : 'text', 'text' : u'うーん、ないかも。。'}]
            else:
                respmsgs = self.makeResultMsg(rs)

        assert(isinstance(respmsgs, list))

        headers = {
            'Content-type': 'application/json',
            'Authorization': 'Bearer ' + self.conf.getLineBotToken()
        }
        data = {
            'replyToken' : token,
            'messages' : respmsgs
        }
        logging.info(data)

        return requests.post('https://api.line.me/v2/bot/message/reply', headers = headers, json = data)

    def makeResultMsg(self, rs):
        #print(rs)
        columns = [{
            "thumbnailImageUrl": r['image'],
            #"title": r['title'][:40],
            "text": r['title'][:60],
            "actions": [
                {
                    "type": "uri",
                    "label": "View detail",
                    "uri": r['url']
                }
            ]
        } for r in rs]

        rc = {
            "type": "template",
            "altText": "this is a carousel template",
            "template": {
                "type": "carousel",
                "columns": columns
            }
        }
        #print(rc)
        return [rc]

    def processMessageText(self, intxt):
        logging.info("intxt = %s" % (intxt,))

        bkgenres = []
        words = []
        adverbs = []

        logging.info(self.m.parse(''))
        node = self.m.parseToNode(intxt)
        while node:
            #print (node.surface, node.feature)
            f = node.feature.split(',')
            #print (f)
            kw = f[-3]
            if kw == r'*':
                kw = node.surface
            knd = f[0]
            #print(knd)
            if knd in (u'名詞',):
                kwu = kw.upper()
                if kwu in self.cat.getNames():
                    bkgenres.append(self.cat.getCatID(kwu))
                else:
                    words.append(kw)
            elif knd in (u'形容詞', u''):
                adverbs.append(kw)
            node = node.next

        if words:
            # workaround
            words = [w for w in words if len(w) > 1]
            words.sort(key=len, reverse=True)

        # for debug
        logging.info(bkgenres)
        logging.info(words)
        logging.info(adverbs)

        rs = None
        if len(bkgenres) > 0:
            if not words:
                # ranking
                ge = self.consolidateGenre(bkgenres)
                logging.info('== ranking')
                rs = self.bkc.ranking(genre = ge)
            else:
                # genre keyword search
                ge = self.consolidateGenre(bkgenres)
                so = self.adverbToSortOrder(adverbs)
                logging.info('== genre search')
                rs = self.bkc.search(' '.join(words), genre = ge, order = so)
        else:
            # free keyword search
            logging.info('== keyword search')
            so = self.adverbToSortOrder(adverbs)
            rs = self.bkc.search(' '.join(words), order = so)

        return rs

    def consolidateGenre(self, genres):
        # by common predecessor, similarity
        return genres[0]

    def adverbToSortOrder(self, adverbs):
        if not adverbs:
            return 'standard'

        # TODO: should use word2vec
        adv = adverbs[0]
        if adv == u'新しい':
            return '-releaseDate'
        elif adv == u'古い':
            return '+releaseDate'
        elif adv == u'安い':
            return '+itemPrice'
        elif adv == u'高い':
            return '-itemPrice'
        elif adv == u'おすすめ':
            return 'sales'
        # reviewed/well rated TBD

        return 'standard'

    def mecab_list(self, s):
        '''return list of mecab analysis'''
        s = self.m.parse(s)
        r = [word.split(',') for word in s.replace('\t', ',').split('\n')[:-2]]
        return r


if __name__ == '__main__':
    main()
