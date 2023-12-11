from flask import Flask, render_template, session
from flask_session import Session
from datetime import datetime
import requests
from plot_utils import linguistic_plot, word_count_distribution_plot

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route('/')
def index():
    url = "https://us-central1-news-analyzer-403505.cloudfunctions.net/get_news?freshness=any&categories=world&max_results=10&stats=1"
    response = requests.get(url)
    response_json = response.json()
    session['current_article'] = response_json

    for item in response_json:
        datetime_str = item['pubDate']
        date_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        item['pubDate'] = date_obj.strftime("%d %b, %Y %H:%M")
    
    return render_template('index.html', news_objects=response_json)

@app.route('/article/<article_name>')
def single_article(article_name):
    article = {}
    for item in session['current_article']:
        if item['article_id'] == article_name:
            article = item
            break
    if article:
        linguistic_figure = linguistic_plot(article)
        word_dist_figure = word_count_distribution_plot(article)
        article['linguistic_figure'] = linguistic_figure
        article['word_dist_figure'] = word_dist_figure
    return render_template('singlearticle.html', article=article)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
