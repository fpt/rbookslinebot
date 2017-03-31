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
