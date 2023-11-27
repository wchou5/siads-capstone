from flask import Flask, render_template
from datetime import datetime
import requests

app = Flask(__name__)

@app.route('/')
def index():
    url = "https://us-central1-news-analyzer-403505.cloudfunctions.net/get_news?freshness=180&max_results=10"
    response = requests.get(url)
    response_json = response.json()
    # print(type(response_json[0]['pubDate']))
    # print(response_json[0]['pubDate'])

    # fetch last 24 hrs artciles
    # sort in desc based on time

    for item in response_json:
        datetime_str = item['pubDate']
        date_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        item['pubDate'] = date_obj.strftime("%d %b, %Y %H:%M")
    
    return render_template('index.html', news_objects=response_json)

@app.route('/{article_name}')
def single_article():
    return render_template('index.html', news_objects=response_json)