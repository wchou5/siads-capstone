import functions_framework

# %%
from goose3 import Goose
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re
import gcsfs
import fsspec
import pytz

# %%
AD_KEYWORDS = [
    'ad', 'banner', 'promo', 'sponsor', 'googlead',
    'advertisement', 'affiliate', 'adblock', 'social', 'READ MORE'
]

CSS_SELECTORS_TO_REMOVE = [
    #'.class-to-remove',
    #'#id-to-remove',
    #'div[style*="display: none"]',
    '.mor-link',
    'p em strong',
    '.img-container.shareable-item.wp-caption'
]

# %%
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

def remove_selectors(soup, selectors):
    for selector in selectors:

        for element in soup.select(selector):
            #print(selector)
            element.decompose()

    return soup

def preprocess_html(url, keywords, selectors):

    g = Goose()
    article = g.extract(url=url)
    raw_html_content = article.raw_html

    soup = BeautifulSoup(raw_html_content, 'html.parser')

    # Pre-process HTML with attributes and CSS selectors
    soup = clean_with_attributes(soup, keywords)
    soup = remove_selectors(soup, selectors)

    return str(soup)


@functions_framework.cloud_event
def main_execution(cloud_event):
    data = cloud_event.data
    bucket = data["bucket"]
    file_path = data["name"]

    if bucket == "news-project-file-storage" and "articles" in file_path and ".csv" in file_path:

        # %%
        df = pd.read_csv('gs://'+bucket+'/'+file_path)
        # %%
        # for index, row in df.iterrows():
        #     df.loc[index, 'clean_content'] = index

        # %%

        #print("df len: ", len(df))
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

        # %%
        # df.isna().sum()

        # %%
        # len(error_url)

        # %%
        df = df[~df['clean_content'].isna()]

        # %%
        df['clean_content_len'] = df['clean_content'].apply(lambda x: len(x))

        # %%
        # df['clean_content_len'].describe()

        # %%
        df = df[df['clean_content_len'] > 500]

        # %%
        # df.shape
        # df['clean_content_len'].describe()

        # %%
        filename_match = re.search(r"/(\d{4}_\d{2}_\d{2}/[^/]+\.csv)", file_path)
        filename = filename_match.group(0)
        if len(df):
            df.to_csv(f'gs://news-project-outputs/newsdata_scraped_content'+filename, index=False)

            print('content clean done: '+ filename)



"""
# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")
"""