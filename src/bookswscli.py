#!/usr/bin/env python
# coding:utf-8

import pprint
import requests
from argparse import ArgumentParser
import os
import sys
import csv
import logging

logging.basicConfig(level=logging.DEBUG)


def main():
    parser = ArgumentParser()
    parser.add_argument('query', nargs='?', help='query string')
    args = parser.parse_args()

    qstr = args.query

    cat = BooksCategory()
    cat.load()
    #print(cat.getNames())
    return

    bc = BooksWSClient()
    #bc.ranking('000')
    bc.totalsearch(u'コナン')


class BooksCategory():
    def __init__(self):
        self.cat = dict()
        pass

    def load(self):
        here = os.path.dirname(__file__)
        tsvfile = os.path.join(here, r'../data/books_category.tsv')

        with open(tsvfile, 'r', encoding='utf-8') as f:
            tsv = csv.reader(f, delimiter = '\t')
              
            for row in tsv:
                #print(", ".join(row))
                name = row[1]
                self.cat[name] = row[0]
                if u'・' in name:
                    nms = name.split(u'・')
                    for n in nms:
                        if n in self.cat:
                            if len(self.cat[n]) > len(row[0]):
                                self.cat[n] = row[0]
                        else:
                            self.cat[n] = row[0]

    def getNames(self):
        return self.cat.keys()

    def getCatID(self, name):
        return self.cat[name]


class BooksWSClient():
    def __init__(self, appid):
        self.appid = appid

    def ranking(self, genre='000'):
        p = {
            'hits': 3,
            'page': 1,
            'period': 0
        }
        uri = "https://api.books.rakuten.co.jp/ranking/1/%s/hourly.json" % (genre,)
        logging.info(uri)
        r = requests.get(uri, params=p)
        logging.info(r.status_code)
        if r.status_code > 200:
            # fall back to search
            return self.search(None, genre = genre)
        return self.processResponse(r)

    # [standard, sales, -itemPrice, +itemPrice, -releaseDate, +releaseDate, reviewCount, reviewAverage]
    def search(self, keyword, genre='000', order='standard'):
        p = {
            'applicationId': self.appid,
            'booksGenreId': genre,
            'hits': 3,
            'sort': order
        }
        if keyword:
            p['keyword'] = keyword
        uri = "https://app.rakuten.co.jp/services/api/BooksTotal/Search/20130522"
        logging.info(uri)
        r = requests.get(uri, params=p)
        logging.info(r.status_code)
        return self.processResponse(r)

    def processResponse(self, r):
        if r.status_code is not 200:
            logging.warn("error response %d" % (r.status_code,))
            return

        rj = r.json()
        if rj['hits'] < 1:
            logging.warn("no hit")
            return

        logging.info(rj)
        itms = []
        if 'Items' in rj:
            for i in rj['Items']:
                itms.append({
                    'title' : i['Item']['title'],
                    'price' : i['Item']['itemPrice'],
                    'image' : i['Item']['largeImageUrl'].replace('http', 'https'),
                    'url'   : i['Item']['itemUrl']
                })
        elif 'data' in rj:
            for i in rj['data']:
                itms.append({
                    'title' : i['title'],
                    'price' : i['price'],
                    'image' : i['image_url'].replace('http', 'https'),
                    'url'   : i['url']
                })

        logging.info(itms)
        return itms


if __name__ == '__main__':
    main()
