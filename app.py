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
# Rota de download (API)
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
# Inicialização local
# =========================
if __name__ == "__main__":
    app.run()
