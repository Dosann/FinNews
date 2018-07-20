# -*- coding:utf-8 -*-

from flask import Flask
from flask import request, render_template, send_from_directory
import json
import services
from gevent import monkey
monkey.patch_all()
app = Flask(__name__, template_folder='static')

svs = services.service()

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/api/hotwords', methods = ['GET'])
def get_hotwords():
    days = request.args.get('days', type = int)
    ### TODO
    return '你申请了%d天的热词数据.'%days

@app.route('/api/word_temperature', methods = ['GET'])
def get_word_temperature():
    days = request.args.get('days', type = int)
    word = request.args.get('word', type = str)
    ### TODO
    return '你申请了%d天内%s这个词的热度数据.'%(days, word)

@app.route('/api/stock_index', methods = ['GET'])
def get_stock_index():
    ### TODO
    return '你申请了股指数据.'

@app.route('/api/newest_article', methods = ['GET'])
def get_newest_article():
    return svs.get_newest_article()

@app.route('/api/recent_hotwords', methods = ['GET'])
def get_recent_hotwords():
    time_period = request.args.get('days', type = int)
    articles = svs.get_recent_articles(time_period = time_period)
    if articles is not None:
        articles_inone = '.'.join(list(map(lambda x:x[2], articles)))
        hotwords = svs.get_keywords(articles_inone, num_keywords = 100)
    else:
        hotwords = [["NO RECENT NEWS!", 50]]
    return json.dumps(hotwords)

@app.route('/api/wordfreq', methods = ['GET'])
def get_wordfreq():
    period = request.args.get('period', type = str)
    word = request.args.get('word', type = str)
    return svs.get_wordfreq(period, word)

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 80, threaded = True)
