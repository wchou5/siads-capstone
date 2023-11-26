import pandas as pd
import re

def cleanup_article(text):
  sentences = re.split('(?<=!\s)|(?<=\.\s)|(?<=\?\s)|(?<=--)|\|', text)
  cleaned = []
  remove_next = False

  for i in range(0, len(sentences)):
    if remove_next == True:
      remove_next = False
      continue
    sent = sentences[i].strip()
    sent = re.sub('.*\((.*)\)\s--', '', sent)
    if sent in skip_next:
      remove_next = True
      continue
    if i < 5 and sent.startswith('and'):
      continue
    if any(x in sent.lower() for x in remove):
      continue
    if i == 0:
      sent = re.sub('.*\(CNN\)', '', sent)
    if re.search('[a-zA-Z\d]', sent):
      cleaned.append(sent.strip())

  return ' '.join(cleaned)


skip_next = ['By .', 'PUBLISHED: .', 'UPDATED: .']
remove = ['click here', 'follow @', 'last updated', 'scroll down']

df = pd.read_csv('data/original_dataset.csv')
df = df[['article', 'highlights']]

df['article'] = df.apply(lambda x: cleanup_article(x['article']), axis = 1)
df['highlights'] = df.apply(lambda x: x['highlights'].replace('\n', ' '), axis = 1)

df['article_wordcount'] = df['article'].str.count(' ') + 1
df['summary_wordcount'] = df['highlights'].str.count(' ') + 1
df['summary_sentcount'] = df['highlights'].str.count('\. ') + 1

df.to_csv('output/clean_df_output.csv', index = False)