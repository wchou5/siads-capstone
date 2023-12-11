import functions_framework
import pandas as pd
import pandas_gbq
import gcsfs
import fsspec

from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords

import spacy
import numpy as np
import json

# Define constants for project and table IDs
project_id = "news-analyzer-403505"
table_id = 'news_dataset.news_summaries_v2'

# Custom JSON converter to handle int64 types
def default_converter(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    raise TypeError

# Function to summarize text using Gensim's summarize method
def gensim_summary(text):
  try:
    return summarize(text, word_count=108)
  except: 
    return ""

# Load Spacy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Function to calculate the percentage of different POS tags in a text
def spacy_pos_percentage(text):
    doc = nlp(text)

    counts = {
        'NOUN': 0,
        'VERB': 0,
        'ADJ': 0,
        'ADV': 0,
        'TOTAL': 0
    }

    for token in doc:
        if token.pos_ in counts:
            counts[token.pos_] += 1
        counts['TOTAL'] += 1

    return json.dumps({
        'noun_percentage': (counts['NOUN'] / counts['TOTAL']) * 100,
        'verb_percentage': (counts['VERB'] / counts['TOTAL']) * 100,
        'adj_percentage': (counts['ADJ'] / counts['TOTAL']) * 100,
        'adv_percentage': (counts['ADV'] / counts['TOTAL']) * 100,
    }, default=default_converter)


# Function to calculate the distribution of word lengths in a text
def text_word_length_cdf(text):
    doc = nlp(text)

    words = [token.text for token in doc if not token.is_punct]
    total_words = len(words)

    percentage_word_count = {}

    for i in range(10, 101, 10):
        count = int(round((i / 100) * total_words))
        percentage_word_count[f"p_{i}"] = count

    return json.dumps(percentage_word_count, default=default_converter)


# Function to extract and count named entities in a text
def show_ents(article):
    doc = nlp(article)
    ent_dict = {}
    if doc.ents:
        for ent in doc.ents:
            if ent.label_ in ent_dict:
                ent_dict[ent.label_] += 1
            #print(ent.text+' - '+ent.label_
            else:
                ent_dict[ent.label_] = 1
    return json.dumps(ent_dict, default=default_converter)


# Cloud function to process and store news data
@functions_framework.cloud_event
def main_execution(cloud_event):
    data = cloud_event.data
    bucket = data["bucket"]
    file_path = data["name"]

    if bucket == "news-project-outputs" and "articles" in file_path and ".csv" in file_path:
      df = pd.read_csv('gs://'+bucket+'/'+file_path)

      df["news_fetch_date"] = pd.to_datetime(df["news_fetch_date"])
      df["news_fetch_timestamp"] = pd.to_datetime(df["news_fetch_timestamp"])

      df['summary'] = df['clean_content'].apply(gensim_summary)

      df['clean_content_pos'] = df['clean_content'].apply(spacy_pos_percentage)
      df['summary_pos'] = df['summary'].apply(spacy_pos_percentage)

      df['clean_content_cdf'] = df['clean_content'].apply(text_word_length_cdf)
      df['summary_cdf'] = df['summary'].apply(text_word_length_cdf)

      df['summary_ent'] = df['summary'].apply(show_ents)

      columns_to_drop = ['description', 'content', 'clean_content']
      df.drop(columns=columns_to_drop, inplace=True)
      
      if len(df):
        pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists="append")
        print('df pushed to bq:'+ file_path)


      
      
