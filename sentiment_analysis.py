
import pandas as pd
from transformers import pipeline


sentiment_analysis = pipeline("sentiment-analysis")

def analyze_transcripts(file_path):
    with open(file_path, 'r') as file:
        transcripts = file.readlines()

    results = []
    for transcript in transcripts:
        sentiment = sentiment_analysis(transcript)[0]
        results.append({
            'transcript': transcript.strip(),
            'label': sentiment['label'],
            'score': sentiment['score']
        })

    return pd.DataFrame(results)

def determine_overall_sentiment(df):
    sentiment_counts = df['label'].value_counts()
    total_count = len(df)
    positive_count = sentiment_counts.get('POSITIVE', 0)
    negative_count = sentiment_counts.get('NEGATIVE', 0)

    if positive_count / total_count > 0.5:
        return "POSITIVE"
    else:
        return "NEGATIVE"
