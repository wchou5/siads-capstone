import pandas as pd
import datetime
import evaluate
bertscore = evaluate.load("bertscore")
rouge = evaluate.load('rouge')
bleu = evaluate.load('bleu')
meteor = evaluate.load('meteor')


def eval_rouge(summary, reference):
  results =  rouge.compute(predictions=[summary], references=[reference])
  return results['rouge1'], results['rouge2'], results['rougeL'], results['rougeLsum']


def eval_bleu(summary, reference):
  return bleu.compute(predictions=[summary], references=[reference], max_order = 2)['bleu']


def eval_bertscore(summary, reference):
  return bertscore.compute(predictions=[summary], references=[reference], lang="en")['f1'][0]


def eval_meteor(summary, reference):
  return meteor.compute(predictions=[summary], references=[reference])['meteor']


df = pd.read_csv('output/create_summaries_output.csv')
df = df[['highlights', 'pysum', 'gensim', 'spacy', 'cos_sim']]
df = df[df['cos_sim'] != '---']
df = df.dropna()

for col in ['pysum', 'gensim', 'spacy', 'cos_sim']:
  df['results'] = df.apply(lambda x: eval_rouge(x['highlights'], x[col]), axis = 1)
  df[[col + '_rouge1', col + '_rouge2', col + '_rougeL', col + '_rougeLsum']] = pd.DataFrame(df['results'].tolist(), index = df.index)
  df[col + '_bleu'] = df.apply(lambda x: eval_bleu(x['highlights'], x[col]), axis = 1)
  df[col + '_bert'] = df.apply(lambda x: eval_bertscore(x['highlights'], x[col]), axis = 1)
  df[col + '_meteor'] = df.apply(lambda x: eval_meteor(x['highlights'], x[col]), axis = 1)

df.to_csv('output/evaluate_summaries_output.csv', index = False)