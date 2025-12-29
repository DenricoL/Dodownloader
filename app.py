from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")

    if not url or "instagram.com" not in url:
        return jsonify({"error": "Invalid Instagram URL"}), 400

    video_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_FOLDER, video_id)

    ydl_opts = {
        "outtmpl": f"{output}.%(ext)s",
        "format": "mp4",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.startswith(video_id):
                return send_file(
                    os.path.join(DOWNLOAD_FOLDER, file),
                    as_attachment=True
                )

        return jsonify({"error": "Error locating video"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
