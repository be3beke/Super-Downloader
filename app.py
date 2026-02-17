from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import io

app = Flask(__name__)

# Ensure a temporary directory exists for processing
DOWNLOAD_FOLDER = 'temp_downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    url = request.json.get('url')
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'formats': 'Success'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    mode = request.args.get('mode') # 'video' or 'audio'

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if mode == 'video' else 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'noplaylist': True,
    }

    if mode == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        
        # If audio, the extension changes to .mp3 after post-processing
        if mode == 'audio':
            file_path = os.path.splitext(file_path)[0] + '.mp3'

        return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
