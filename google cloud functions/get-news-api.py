import functions_framework
from pandas_gbq import read_gbq

path_to_bigquery_table = 'YOUR PATH HERE' # e.g. `news-analyzer-403505.news_dataset.news_summaries`

# Function to fetch news data based on specified parameters from BigQuery database
def fetch_news_data(freshness, categories, max_results=20):

    query = """
    SELECT
        news_fetch_timestamp,
        title,
        link,
        creator,
        pubDate,
        image_url,
        category,
        summary
    FROM
        
    """ + path_to_bigquery_table

    where_conditions = []

    if freshness.isdigit():
        where_conditions.append("news_fetch_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {} MINUTE)".format(freshness))
    elif freshness.lower() == "any":
        pass
    else:
        pass
        
    if categories:
        category_filter = "category IN (" + ', '.join(["'" + str(category) + "'" for category in categories]) + ")"
        where_conditions.append(category_filter)

    if where_conditions:
        query += "WHERE " + " AND ".join(where_conditions) + " "

    query += "ORDER BY news_fetch_timestamp DESC, pubDate DESC\nLIMIT {}".format(max_results)

    news_data_df = read_gbq(
        query,
        dialect='standard',
        project_id='news-analyzer-403505',
        )

    query_news_data = news_data_df.to_dict(orient='records')

    return query_news_data

#Function to handle HTTP requests and preparing GET API
@functions_framework.http
def hello_http(request):

    request_json = request.get_json(silent=True)
    request_args = request.args

    freshness_param = request_args.get('freshness', default="any")
    categories_param = request_args.get('categories', default=None)
    max_results_param = request_args.get('max_results', default=None)

    if categories_param and isinstance(categories_param, str):
        categories = categories_param.split(',')
    else:
        categories = None

    max_results = int(max_results_param) if max_results_param.isdigit() else 20

    news_data = fetch_news_data(freshness_param, categories, max_results)

    return news_data
