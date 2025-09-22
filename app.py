from flask import Flask, request, jsonify, render_template, send_from_directory
import yt_dlp
import os

app = Flask(__name__, static_folder='static')

# yt-dlp options
ydl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return jsonify([])

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(
                f"ytsearch5:{query}", download=False)["entries"]

        songs = []
        for r in results:
            songs.append({
                "title": r.get("title"),
                "url": r.get("webpage_url"),
                "thumbnail": r.get("thumbnail"),
                "id": r.get("id")
            })
        return jsonify(songs)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/stream/<video_id>")
def stream(video_id):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False)
        return jsonify({"url": info["url"]})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/static/service-worker.js')
def serve_service_worker():
    response = send_from_directory(app.static_folder, 'service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response


@app.route('/static/manifest.json')
def serve_manifest():
    response = send_from_directory(app.static_folder, 'manifest.json')
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/static/icons/<path:filename>')
def serve_icon(filename):
    return send_from_directory(os.path.join(app.static_folder, 'icons'), filename)


if __name__ == "__main__":
    app.run(debug=True)
