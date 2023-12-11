import base64
import functions_framework
import gcsfs
import fsspec

from datetime import datetime, date
import pandas as pd
import newspaper
from newspaper import news_pool
import time
from newspaper import Article
from bs4 import BeautifulSoup
from configparser import ConfigParser
from newsdataapi import NewsDataApiClient
from collections import Counter
import requests
import pytz

# Define categories for news articles
categories = ['business', 'entertainment', 'environment', 'food', 'health', 
            'politics', 'science', 'sports', 'world', 'tourism', 'technology', 'top']

categories1 = categories[:5]
categories2 = categories[5:10]

# API Key for NewsData API
API_KEY = 'ENTER API KEY HERE'
api = NewsDataApiClient(apikey=API_KEY)

# Function to fetch all pages of news articles for a given category
def get_all_page_response2(category, domain_url=None):
    page = None
    responses_results = []
    count = 0
    while True:
        if domain_url:
            response = api.news_api(domainurl = domain_url, category=category, page = page, language='en', timeframe=1, full_content=True) #added time frame, full_content
        else:
            response = api.news_api(category=category, page = page, language='en', timeframe=1, full_content=True) #added language, time frame, full_content
        responses_results.append(response)
        page = response.get('nextPage',None)
        if not page:
            break
        if count >= 4: #updated count limit from 50 to 4
            break
        count += 1
            
    return responses_results


# Function to create a DataFrame from the API responses
def create_response_df2(responses):
    flattened_data = []
    print(len(responses))
    for page in responses:
        for news in page['results']:
            flattened_result = {}

            for key, value in news.items():
                if isinstance(value, list):
                    flattened_result[key] = ', '.join(map(str, value))
                else:
                    flattened_result[key] = value
            flattened_data.append(flattened_result)

    df = pd.DataFrame(flattened_data)

    if len(df):
        df = df[df["language"] == "english"]
        return df
    else:
        return pd.DataFrame()

# Cloud function to execute the main process
@functions_framework.cloud_event
def main_execution(cloud_event):
    print('main execution started')
    #print(base64.b64decode(cloud_event.data["message"]["data"]))
    # %%
    response_all_news_cat1 = get_all_page_response2(categories1)
    print('cat 1 done')
    response_all_news_cat2 = get_all_page_response2(categories2)
    print('cat 2 done')

    # %%
    df_all_news1 = create_response_df2(response_all_news_cat1)
    df_all_news2 = create_response_df2(response_all_news_cat2)

    
    df_all_news = pd.concat([df_all_news1, df_all_news2])
    print('df merged')

    # %%
    
    #df_all_news.to_csv('Articles_'+today_date+'.csv', index=False)

    dubai_time_zone = pytz.timezone('Asia/Dubai')
    current_time_dubai = datetime.now(dubai_time_zone)

    today_date = current_time_dubai.strftime('%Y_%m_%d')
    today_date_hour_min_sec = current_time_dubai.strftime('%Y_%m_%d-%H-%M-%S')

    df_all_news['news_fetch_timestamp'] = current_time_dubai
    df_all_news['news_fetch_date'] = current_time_dubai.strftime('%Y-%m-%d')

    initial_cols = ['news_fetch_date', 'news_fetch_timestamp']

    column_order = initial_cols + [col for col in df_all_news.columns if col not in initial_cols]
    df_all_news = df_all_news[column_order]

    if len(df_all_news):
        print('sending to gsc...')

        df_all_news.to_csv('gs://news-project-file-storage/newsdata_api_export/'+ today_date +'/articles_'+today_date_hour_min_sec+'.csv', index=False)

        print('articles_'+today_date_hour_min_sec+'.csv created')
    print('execution completed: '+ today_date_hour_min_sec)




