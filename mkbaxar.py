from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import yt_dlp
import shutil

app = Flask(__name__)

# Pasta de downloads
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Caminho do ffmpeg
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

if not shutil.which("ffmpeg") and not os.path.isfile(FFMPEG_PATH):
    raise SystemExit("FFmpeg não encontrado! Ajuste o caminho no app.py.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")
    formato = data.get("formato")
    qualidade = data.get("qualidade")
    nome_arquivo = data.get("nome")

    if not url:
        return jsonify({"status": "erro", "msg": "URL não informada!"})

    if formato == "mp4":
        if not nome_arquivo:
            nome_arquivo = "video_baixado.mp4"
        elif not nome_arquivo.lower().endswith(".mp4"):
            nome_arquivo += ".mp4"
        saida = os.path.join(DOWNLOAD_FOLDER, nome_arquivo)

        qualidades_map = {
            "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "4k": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "auto": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
        }
        formato_final = qualidades_map.get(qualidade, "best")

        opcoes = {
            "outtmpl": saida,
            "format": formato_final,
            "noplaylist": True,
            "merge_output_format": "mp4",
            "ffmpeg_location": FFMPEG_PATH,
            "writethumbnail": True,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ],
        }
    else:  # MP3
        if not nome_arquivo:
            nome_arquivo = "audio_baixado.mp3"
        elif not nome_arquivo.lower().endswith(".mp3"):
            nome_arquivo += ".mp3"
        saida = os.path.join(DOWNLOAD_FOLDER, nome_arquivo)

        opcoes = {
            "outtmpl": saida,
            "format": "bestaudio/best",
            "noplaylist": True,
            "writethumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                    "ffmpeg_location": FFMPEG_PATH
                },
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ],
        }

    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            ydl.download([url])
        return jsonify({"status": "ok", "msg": "Download concluído!", "arquivo": nome_arquivo})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)})

@app.route("/downloads/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)