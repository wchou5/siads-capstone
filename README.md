Install the libraries listed in requirements.txt (make sure to match version if listed)

For creating the summaries and evaluation:
1. Run summarization/clean_df.py (will read from train.csv and create output/clean_df_output.csv)
2. Run summarization/create_summaries.py (will read from output/clean_df_output.csv and create output/create_summaries_output.csv)
3. Run summarization/evaluate_summaries.py (will read from output/create_summaries_output.csv and create output/evaluate_summaries_output.csv)

For creating visuals:
1. After summarization/clean_df.py, run summary_stats.ipynb (will read from output/clean_df_output.csv)
2. After summarization/evaluate_summaries.py, run evaluation_stats.ipynb (will read from output/evaluate_summaries_output.csv)