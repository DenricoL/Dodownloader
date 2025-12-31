from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid
import threading
import time


app = Flask(__name__)

# =========================
# Pasta de downloads
# =========================
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# =================================
# cookies de variáveis de ambiente
# ==================================
def load_cookies_from_env(env_name, file_name):
    cookies = os.getenv(env_name)
    if not cookies:
        print(f"⚠️ Variável de ambiente {env_name} não encontrada")
        return None

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(cookies)

    print(f"✅ Cookies carregados: {file_name}")
    return file_name


TIKTOK_COOKIE_FILE = load_cookies_from_env("TIKTOK_COOKIES", "cookies_tktk.txt")
YOUTUBE_COOKIE_FILE = load_cookies_from_env("YOUTUBE_COOKIES", "cookies_yt.txt")


# =========================
# Deletar arquivo depois do envio
# =========================
def delete_file_later(path, delay=15):
    def task():
        time.sleep(delay)
        if os.path.exists(path):
            os.remove(path)
            print(f"🗑️ Arquivo apagado: {path}")

    threading.Thread(target=task, daemon=True).start()


# =========================
# Rota principal (front-end)
# =========================
@app.route("/")
def home():
    return app.send_static_file("index.html")


# =========================
# Instagram Downloader
# =========================
@app.route("/download", methods=["POST"])
def download_instagram():
    data = request.get_json()
    url = data.get("url")

    if not url or "instagram.com" not in url:
        return jsonify({"error": "Invalid Instagram URL"}), 400

    video_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_FOLDER, video_id)

    ydl_opts = {
        "outtmpl": f"{output}.%(ext)s",
        "format": "mp4",
        "quiet": True,
        "max_filesize": 150 * 1024 * 1024
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

        return jsonify({"error": "Error locating video"}), 500

    except Exception as e:
        print("Erro Instagram:", e)
        return jsonify({"error": "Failed to download Instagram video."}), 500


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
        "cookiefile": TIKTOK_COOKIE_FILE,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.tiktok.com/"
        }
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
        return jsonify({"error": "Failed to download TikTok video."}), 500


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
        "noplaylist": True
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
        
        "quiet": True,
        "noplaylist": True,
        
        "extractor_args": {
        "youtube": {
            "player_client": ["android"]
            }
        },
        
        "user_agent": (
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"
        ),
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
        return jsonify({"error": "Failed to download YouTube video."}), 500


# =========================
# Inicialização local
# =========================
if __name__ == "__main__":
    app.run()
