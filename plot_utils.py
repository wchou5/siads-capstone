import plotly.graph_objects as go
import plotly
import json

def linguistic_plot(article):
    clean_content_pos = json.loads(article["clean_content_pos"])
    summary_pos = json.loads(article["summary_pos"])
    clean_content_cdf = json.loads(article["clean_content_cdf"])
    summary_cdf = json.loads(article["summary_cdf"])

    pos_categories = ['Noun', 'Verb', 'Adjective', 'Adverb']

    pos_values_clean = [clean_content_pos["noun_percentage"],
                        clean_content_pos["verb_percentage"],
                        clean_content_pos["adj_percentage"],
                        clean_content_pos["adv_percentage"]]

    pos_values_summary = [summary_pos["noun_percentage"],
                        summary_pos["verb_percentage"],
                        summary_pos["adj_percentage"],
                        summary_pos["adv_percentage"]]

    fig1 = go.Figure(data=[
        go.Bar(name='Original', x=pos_categories, y=pos_values_clean),
        go.Bar(name='Summary', x=pos_categories, y=pos_values_summary)
    ])


    fig1.update_layout(
        xaxis_title='Word types',
        yaxis_title='Percentage share of word types',
        width=500,
        height=400
    )

    plot_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return plot_json


def word_count_distribution_plot(article):
    clean_content_cdf = json.loads(article["clean_content_cdf"])
    summary_cdf = json.loads(article["summary_cdf"])

    percentages = list(clean_content_cdf.keys())

    clean_content_values = [clean_content_cdf[key] for key in percentages]

    summary_values = [summary_cdf[key] for key in percentages]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(y=percentages, x=clean_content_values, mode='lines+markers', line_shape='spline', name='Original'))
    fig2.add_trace(go.Scatter(y=percentages, x=summary_values, mode='lines+markers', line_shape='spline', name='Summary'))

    fig2.update_layout(
        xaxis_title='Word count',
        yaxis_title='Percentage of text',
        width=500,
        height=400
    )

    plot_json = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return plot_json