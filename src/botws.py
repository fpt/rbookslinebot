#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os, sys
import json, codecs
import requests
import flask
from flask import Flask, redirect, url_for, session, request, render_template
from linebot import BooksLineBot, BooksBotConfig
import configparser


logging.basicConfig(level=logging.DEBUG)

conf = BooksBotConfig()
bot = BooksLineBot(conf)
#sys.exit(0)

root_dir = os.path.dirname(os.path.abspath(__file__))
tmpl_dir = os.path.join(root_dir, 'tmpl')
static_dir = os.path.join(root_dir, 'static')
app = flask.Flask(__name__, template_folder=tmpl_dir, static_folder=static_dir)


@app.route("/")
def index():
    return "Hello world."


@app.route("/rae_auth", methods=['GET'])
def rae_auth():
    p = {
      'response_type': 'code',
      'client_id': '1010340428247090313',
      'scope': 'rakuten_favoritebookmark_read',
      'redirect_uri': 'https://fjmt.me/books_line_bot/rae_auth_return'
    }
    r = requests.get('https://app.rakuten.co.jp/services/authorize', allow_redirects=False, params=p)
    logging.info(r)
    return redirect(r.headers['Location'], code=r.status_code)

@app.route("/rae_auth_return", methods=['GET'])
def rae_auth_return():
    code = request.args.get('code', '')
    d = {
      'grant_type': 'authorization_code',
      'client_id': '1010340428247090313',
      'client_secret': '69d817923e05505b85577e2fb69d2ebedde8ad78',
      'code': code,
      'scope': 'rakuten_favoritebookmark_read',
      'redirect_uri': 'https://fjmt.me/books_bot/rae_auth_return'
    }
    r = requests.post('https://app.rakuten.co.jp/services/token', data=d)
    print(r)
    json = r.json()
    token = json['access_token']
    return "Return. " + token

# curl -v -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"events":[{}]}' http:/localhost:5100/linebot_webhook/message 

@app.route("/linebot_webhook/message", methods=['POST'])
def on_message():
    assert(request.method == 'POST')
    contenttype = request.headers.get('Content-type')
    logging.info(contenttype)
    if not 'application/json' in contenttype:
        logging.info(contenttype)
        return flask.jsonify(res='error'), 400

    bot.processMessage(request.json)

    return flask.jsonify(res='ok')


def main():
    app.debug = True
    app.run(host='0.0.0.0', port=5100)


if __name__ == "__main__":
    main()

# ref
# http://stackoverflow.com/questions/23915275/how-do-you-add-more-x-axis-ticks-and-labels-to-datetime-axis-using-pythons-boke
