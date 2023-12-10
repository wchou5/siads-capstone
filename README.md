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