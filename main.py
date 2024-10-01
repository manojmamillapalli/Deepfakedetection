from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime
import json
from time import time as current_time
import importlib

app = Flask(__name__)

UPLOAD_FOLDER = 'static/videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        timestamp = int(current_time())
        filename = f"uploaded_video_{timestamp}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(video_path)

        video_path2 = os.path.join(app.config['UPLOAD_FOLDER'], "1" + filename)

        module = importlib.import_module("deepfake_detector")
        function = getattr(module, "run")

        result_from_det, video_path2 = function(video_path, video_path2)
        print(result_from_det)  # Optional: Print accuracy for debugging

        video_info = {
            'name': file.filename,
            'size': f"{os.path.getsize(video_path) / (1024):.2f} KB",
            'user': 'Guest',
            'source': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'accuracy': result_from_det  # Pass accuracy to result page 
        }

        real_percentage = 100 - result_from_det
        fake_percentage = result_from_det

        detection_result = "Real" if real_percentage > fake_percentage else "Fake"

        video_info_json = json.dumps(video_info)

        return redirect(url_for('result', video_info=video_info_json, video_path2=video_path2,
                                detection_result=detection_result, real_percentage=real_percentage,
                                fake_percentage=fake_percentage))


@app.route('/result')
def result():
    video_info_json = request.args.get('video_info')
    video_path2 = request.args.get('video_path2')

    video_info = json.loads(video_info_json)

    accuracy = video_info.get('accuracy', 'N/A')  # Retrieve accuracy from video_info
    detection_result = request.args.get('detection_result')
    real_percentage = request.args.get('real_percentage')
    fake_percentage = request.args.get('fake_percentage')

    return render_template('result.html', video_url=video_path2, video_info=video_info, accuracy=accuracy,
                           detection_result=detection_result, real_percentage=real_percentage,
                           fake_percentage=fake_percentage)

if __name__ == '__main__':
    app.run(debug=True) 