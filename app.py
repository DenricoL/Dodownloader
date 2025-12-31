from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid
import threading
import time


app = Flask(__name__)

# Pasta de downloads
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# =========================
# deletar arquivo depois do envio
# =========================
def delete_file_later(path, delay=15):
    def task():
        time.sleep(delay)
        if os.path.exists(path):
            os.remove(path)
            print(f"Arquivo apagado: {path}")
    threading.Thread(target=task, daemon=True).start()


# =========================
# Rota principal (front-end)
# =========================
@app.route("/")
def home():
    return app.send_static_file("index.html")


# =========================
# Rota de download original (Instagram)
# =========================
@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")

    if not url or "instagram.com" not in url:
        return jsonify({"error": "Invalid Instagram URL"}), 400

    # ID único para o arquivo
    video_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_FOLDER, video_id)

    # Opções do yt-dlp
    ydl_opts = {
        "outtmpl": f"{output}.%(ext)s",
        "format": "mp4",
        "quiet": True,
        "max_filesize": 150 * 1024 * 1024  # limite 150 MB 
    }

    try:
        # Download do vídeo
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Localiza o arquivo baixado
        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.startswith(video_id):
                file_path = os.path.join(DOWNLOAD_FOLDER, file)

                # Envia o arquivo
                response = send_file(file_path, as_attachment=True)

                # Agenda a exclusão
                delete_file_later(file_path)

                return response

        return jsonify({"error": "Error locating video"}), 500

    except Exception as e:
        print("Erro:", e)
        return jsonify({"error": str(e)}), 500
    
# =========================
# TikTok Downloader
# =========================
@app.route("/download/tiktok", methods=["POST"])
def download_tiktok():
    data = request.get_json()
    url = data.get("url")

    if not url or "tiktok.com" not in url:
        return jsonify({"error": "Invalid TikTok URL"}), 400

    video_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_FOLDER, video_id)

    ydl_opts = {
        "outtmpl": f"{output}.%(ext)s",
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "cookiefile": "cookies.txt",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.startswith(video_id):
                file_path = os.path.join(DOWNLOAD_FOLDER, file)

                response = send_file(file_path, as_attachment=True)
                delete_file_later(file_path)

                return response

        return jsonify({"error": "Video not found"}), 500

    except Exception as e:
        print("Erro TikTok:", e)
        return jsonify({
            "error": "Failed to download TikTok video."
        }), 500
        
        
# =========================
# Twitter (X) Downloader
# =========================
@app.route("/download/twitter", methods=["POST"])
def download_twitter():
    data = request.get_json()
    url = data.get("url")

    if not url or ("twitter.com" not in url and "x.com" not in url):
        return jsonify({"error": "Invalid Twitter/X URL"}), 400

    video_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_FOLDER, video_id)

    ydl_opts = {
        "outtmpl": f"{output}.%(ext)s",
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.startswith(video_id):
                file_path = os.path.join(DOWNLOAD_FOLDER, file)

                response = send_file(file_path, as_attachment=True)
                delete_file_later(file_path)

                return response

        return jsonify({"error": "Video not found"}), 500

    except Exception as e:
        print("Erro Twitter:", e)
        return jsonify({"error": "Failed to download Twitter video."}), 500

# =========================
# YouTube Downloader
# =========================
@app.route("/download/youtube", methods=["POST"])
def download_youtube():
    data = request.get_json()
    url = data.get("url")

    if not url or ("youtube.com" not in url and "youtu.be" not in url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    video_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_FOLDER, video_id)

    ydl_opts = {
        "outtmpl": f"{output}.%(ext)s",

        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
        "merge_output_format": "mp4",

        "noplaylist": True,
        "quiet": True,

        "max_filesize": 300 * 1024 * 1024, # limite 300 MB
        
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.startswith(video_id):
                file_path = os.path.join(DOWNLOAD_FOLDER, file)

                response = send_file(file_path, as_attachment=True)
                delete_file_later(file_path)

                return response

        return jsonify({"error": "Video not found"}), 500

    except Exception as e:
        print("Erro YouTube:", e)
        return jsonify({
            "error": "Failed to download YouTube video."
        }), 500


# =========================
# Inicialização local
# =========================
if __name__ == "__main__":
    app.run()
