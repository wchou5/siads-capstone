import functions_framework


from goose3 import Goose
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re
import gcsfs
import fsspec
import pytz

# Define a list of keywords associated with ads and other unwanted elements
AD_KEYWORDS = [
    'ad', 'banner', 'promo', 'sponsor', 'googlead',
    'advertisement', 'affiliate', 'adblock', 'social', 'READ MORE'
]

# Define CSS selectors for elements to be removed from HTML
CSS_SELECTORS_TO_REMOVE = [
    '.mor-link',
    'p em strong',
    '.img-container.shareable-item.wp-caption'
]

# Function to clean HTML content by removing attributes containing ad keywords
def clean_with_attributes(soup, keywords):
    for tag in soup.find_all(True):
        attrs_to_remove = []

        for attr_name, attr_value in tag.attrs.items():

            if any(keyword in attr_name.lower() for keyword in keywords):
                attrs_to_remove.append(attr_name)
                #print(attr_name, attr_value)
            else:
                if isinstance(attr_value, list):
                    attr_value = ' '.join(attr_value)
                if any(keyword in attr_value.lower() for keyword in keywords):
                    attrs_to_remove.append(attr_name)
                    #print(attr_name, attr_value)

        for attr in attrs_to_remove:
            del tag[attr]
    return soup

# Function to remove elements from HTML based on CSS selectors
def remove_selectors(soup, selectors):
    for selector in selectors:

        for element in soup.select(selector):
            #print(selector)
            element.decompose()

    return soup

# Function to preprocess HTML content of a given URL
def preprocess_html(url, keywords, selectors):

    g = Goose()
    article = g.extract(url=url)
    raw_html_content = article.raw_html

    soup = BeautifulSoup(raw_html_content, 'html.parser')

    # Pre-process HTML with attributes and CSS selectors
    soup = clean_with_attributes(soup, keywords)
    soup = remove_selectors(soup, selectors)

    return str(soup)

# Cloud function triggered to process news data
@functions_framework.cloud_event
def main_execution(cloud_event):
    data = cloud_event.data
    bucket = data["bucket"] #define Google cloud storage bucket
    file_path = data["name"] #define Google cloud storage path

    if bucket == "news-project-file-storage" and "articles" in file_path and ".csv" in file_path:

        df = pd.read_csv('gs://'+bucket+'/'+file_path) 
        

        error_url = []
        error_reason = []

        g = Goose()

        for index, row in df.iterrows():
            url = row['link']
            try:
                #print (url)
                cleaned_html = preprocess_html(url, AD_KEYWORDS, CSS_SELECTORS_TO_REMOVE)
                article = g.extract(raw_html=cleaned_html)
                df.loc[index, 'clean_content'] = article.cleaned_text
            except Exception as e:
                error_url.append(url)
                error_reason.append(e)
                df.loc[index, 'clean_content'] = None

        df = df[~df['clean_content'].isna()]

        df['clean_content_len'] = df['clean_content'].apply(lambda x: len(x))

        df = df[df['clean_content_len'] > 500]

        filename_match = re.search(r"/(\d{4}_\d{2}_\d{2}/[^/]+\.csv)", file_path)
        filename = filename_match.group(0)
        if len(df):
            df.to_csv(f'FILE_PATH'+filename, index=False) #define file path to store dataframe

            print('content clean done: '+ filename)

