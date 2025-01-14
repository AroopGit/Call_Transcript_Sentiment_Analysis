from flask import Flask, request, jsonify
import os
from sentiment_analysis import analyze_transcripts, determine_overall_sentiment

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    df = analyze_transcripts(file_path)
    overall_sentiment = determine_overall_sentiment(df)

    results = df.to_dict(orient='records')
    return jsonify({
        'overall_sentiment': overall_sentiment,
        'details': results
    })

if __name__ == '__main__':
    app.run(debug=True)
