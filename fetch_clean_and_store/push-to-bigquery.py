import functions_framework
import pandas as pd
import pandas_gbq
import gcsfs
import fsspec

project_id = "news-analyzer-403505"
table_id = 'news_dataset.news_summaries'

@functions_framework.cloud_event
def main_execution(cloud_event):
    data = cloud_event.data
    bucket = data["bucket"]
    file_path = data["name"]

    if bucket == "news-project-outputs" and "articles" in file_path and ".csv" in file_path:
      df = pd.read_csv('gs://'+bucket+'/'+file_path)

      df["news_fetch_date"] = pd.to_datetime(df["news_fetch_date"])
      df["news_fetch_timestamp"] = pd.to_datetime(df["news_fetch_timestamp"])

      df['summary'] = df['clean_content'].str[:200]

      columns_to_drop = ['description', 'content', 'clean_content']
      df.drop(columns=columns_to_drop, inplace=True)
      
      if len(df):
        pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists="append")
        print('df pushed to bq:'+ file_path)


      
      
