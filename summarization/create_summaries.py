import pandas as pd

from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor

from gensim.summarization.summarizer import summarize

import spacy
nlp = spacy.load("en_core_web_sm")
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from collections import Counter
from heapq import nlargest

import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from nltk.tokenize import sent_tokenize
import numpy as np
import networkx as nx


def use_pysummarization(article):
  auto_abstractor = AutoAbstractor()
  auto_abstractor.tokenizable_doc = SimpleTokenizer()
  auto_abstractor.delimiter_list = ['.']
  abstractable_doc = TopNRankAbstractor()
  result_dict = auto_abstractor.summarize(article, abstractable_doc)
  summarized_sentences = [x for x in result_dict["summarize_result"]]
  
  return ' '.join(summarized_sentences)


def use_gensim(article, summary_len):
  return summarize(article, word_count = summary_len)


# Code is based off of https://medium.com/analytics-vidhya/text-summarization-using-spacy-ca4867c6b744
def use_spacy(article, num_sentences):
  doc = nlp(article)
  keyword = []
  stopwords = list(STOP_WORDS)

  pos_tag = ['PROPN', 'ADJ', 'NOUN', 'VERB']
  for token in doc:
    if token.text in stopwords or token.text in punctuation:
      continue
    if token.pos_ in pos_tag:
      keyword.append(token.text)

  freq_word = Counter(keyword)
  max_freq = Counter(keyword).most_common(1)[0][1]
  for word in freq_word.keys():
    freq_word[word] = (freq_word[word] / max_freq)
  
  sent_strength = {}
  for sent in doc.sents:
    for word in sent:
      if word.text in freq_word.keys():
        if sent in sent_strength.keys():
          sent_strength[sent] += freq_word[word.text]
        else:
          sent_strength[sent] = freq_word[word.text]
    
  summarized_sentences = nlargest(num_sentences, sent_strength, key = sent_strength.get)
  final_sentences = [w.text for w in summarized_sentences]

  return ' '.join(final_sentences)


# Code is based off of https://medium.com/analytics-vidhya/text-summarization-in-python-using-extractive-method-including-end-to-end-implementation-2688b3fd1c8c
def read_article(text):
  sentences = []
  sentences = sent_tokenize(text)

  lemmatized_sentences = []
  for sentence in sentences:
      words = []
      for word in nlp(sentence):
          if not word.is_stop and not word.is_punct:
              words.append(word.lemma_)
      lemmatized_sentences.append(' '.join(words))

  return (lemmatized_sentences, sentences)

def sentence_similarity(sent1, sent2, stopwords = None):
  if stopwords is None: stopwords = []

  sent1 = [w.lower() for w in sent1]
  sent2 = [w.lower() for w in sent2]
  all_words = list(set(sent1 + sent2))

  vector1 = [0] * len(all_words)
  vector2 = [0] * len(all_words)

  for w in sent1:
    if not w in stopwords:
      vector1[all_words.index(w)] += 1

  for w in sent2:
    if not w in stopwords:
      vector2[all_words.index(w)] += 1

  return 1 - cosine_distance(vector1, vector2)

def build_similarity_matrix(sentences, stop_words):
  similarity_matrix = np.zeros((len(sentences), len(sentences)))

  for idx1 in range(len(sentences)):
    for idx2 in range(len(sentences)):
      if idx1 != idx2:
        similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

  return similarity_matrix

def use_cos_sim(text, top_n):
  stop_words = stopwords.words('english')
  summarize_text = []

  sentences, original_sentences = read_article(text)
  sentence_similarity_matrix = build_similarity_matrix(sentences, stop_words)
  sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
  
  try:
    scores = nx.pagerank(sentence_similarity_graph)
  except:
    try:
      scores = nx.pagerank(sentence_similarity_graph, max_iter = 1000)
    except:
      return '---'

  ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(original_sentences)), reverse = True)

  if len(ranked_sentences) < top_n:
     top_n = len(ranked_sentences)
  for i in range(top_n):
    summarize_text.append(ranked_sentences[i][1])

  return ' '.join(summarize_text)


df = pd.read_csv('output/clean_df_output.csv')

df = df[(df['article_wordcount'] >= 100) & (df['article_wordcount'] <= 1000)]
df = df.sample(5000)

textCol = 'article'
num_sentences = 4
num_words = 80 # Assuming 20 words in a sentence

df['pysum'] = df[textCol].apply(lambda x: use_pysummarization(x))
df['gensim'] = df.apply(lambda x: use_gensim(x[textCol], num_words), axis = 1)
df['spacy'] = df.apply(lambda x: use_spacy(x[textCol], num_sentences), axis = 1)
df['cos_sim'] = df.apply(lambda x: use_cos_sim(x[textCol], num_sentences), axis = 1)

df.to_csv('output/create_summaries_output.csv', index = False)