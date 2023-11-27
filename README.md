For creating the summaries and evaluation (found in summarization folder):
1. Install the libraries listed in requirements.txt (make sure to match version if listed).
2. Run clean_df.py (will read from train.csv that is from Kaggle and create clean_df_output.csv)
3. Run create_summaries.py (will read from clean_df_output.csv and create create_summaries_output.csv)
4. Run evaluate_summaries.py (will read from create_summaries_output.csv and create evaluate_summaries_output.csv)

For creating visuals:
1. After clean_df.py, run summary_stats.ipynb (will read from clean_df_output.csv)
2. After evaluate_summaries.py, run evaluation_stats.ipynb (will read from old_evaluate_summaries_output.csv)