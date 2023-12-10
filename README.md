Install the libraries listed in requirements.txt (make sure to match version if listed)

For dataset, download train.csv from https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail/data

For creating the summaries and evaluation:
1. Run summarization/clean_df.py
  - will read from train.csv
  - outputs to output/clean_df_output.csv
  - Runtime: 10 minutes
2. Run summarization/create_summaries.py
  - will read from output/clean_df_output.csv
  - outputs to output/create_summaries_output.csv
  - Runtime: 2 hours
3. Run summarization/evaluate_summaries.py
  - will read from output/create_summaries_output.csv
  - outputs to output/evaluate_summaries_output.csv
  - Runtime: 3 hours

For creating visuals:
1. After summarization/clean_df.py, run summary_stats.ipynb
  - will read from output/clean_df_output.csv
  - visuals can be found in summary_stats_images/
2. After summarization/evaluate_summaries.py, run evaluation_stats.ipynb
  - will read from output/evaluate_summaries_output.csv
  - visuals can be found in evaluation_stats_images/

For creating visuals similar to website:
1. Send a request to url : url = "https://us-central1-news-analyzer-403505.cloudfunctions.net/get_news?freshness=any&categories=world&max_results=10&stats=1"
   - Eg : response = requests.get(url)
   -      response_json = response.json()
   -  This will return the a list of responses. Store a single response. Eg : article = response_json[0]
2. Pass this 'article' variable to linguistic_plot and word_count_distribution_plot which are present in plot_utils.py. This will return the figures for linguistic composition and word count distribution
