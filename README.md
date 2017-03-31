
** behavior

- greeting

- category ranking
(ポジ形容詞 or ポジ動詞) + ジャンル名
おすすめの雑誌は？

- similar item
(context)他には？

- keyword search
カテゴリ+キーワードの場合
乗馬の本ある？
  乗馬 の 本 ある ？

- new sale
新しいマンガは？

** preparation

brew install leveldb mecab mecab-ipadic

apt-get install mecab mecab-ipadic-utf8

sudo apt-get install python3-dev libpng-dev libfreetype6-dev libblas-dev liblapack-dev libatlas-base-dev gfortran
pip install flask requests mecab-python3 gensim pymysql

./init.py

linebot.py

** data

http://www.lr.pi.titech.ac.jp/~takamura/pndic_ja.html


** deploy

gcloud config set project fuj-web
gcloud config set compute/zone us-west1-b
gcloud compute copy-files py-booksbot shrimp:~/proj/
# https://cloud.google.com/compute/docs/gcloud-compute/#set_default_zone_and_region_in_your_local_client
# https://cloud.google.com/compute/docs/instances/transfer-files


curl -v -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"events":[{}]}' https://fjmt.me/books_line_bot/linebot_webhook/message

** SSL cert
brew install certbot
sudo apt-get install certbot python-certbot-apache -t jessie-backports

A 104.199.115.201

a2dissite 000-default-le-ssl
service apache2 reload
service apache2 restart
certbot renew



** extra setup

apt-get install mecab libmecab-dev mecab-ipadic-utf8 libleveldb-dev
sudo apt-get install libapache2-mod-wsgi-py3

sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils
https://github.com/pyenv/pyenv/wiki/Common-build-problems

https://devdocs.line.me/ja/#template-message
http://serverfault.com/questions/456041/getting-client-denied-when-accessing-a-wsgi-graphite-script
http://stackoverflow.com/questions/12081789/pythons-working-directory-when-running-with-wsgi-and-apache