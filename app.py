from flask import Flask, request, jsonify, render_template, send_from_directory
import yt_dlp
import os

app = Flask(__name__, static_folder='static')


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


# yt-dlp options
ydl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "extract_flat": True,  # Better for search results
    "nocheckcertificate": True,
    "geo_bypass": True
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
        print(f"Searching for query: {query}")  # Debug logging
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(
                f"ytsearch5:{query}", download=False)

            if not results or "entries" not in results:
                print("No results found or invalid response")  # Debug logging
                return jsonify({"error": "No results found"})

            entries = results["entries"]
            if not entries:
                return jsonify([])

            songs = []
            for r in entries:
                if r:  # Check if the entry is valid
                    songs.append({
                        "title": r.get("title", "Unknown Title"),
                        "url": r.get("webpage_url", ""),
                        "thumbnail": r.get("thumbnail", ""),
                        "id": r.get("id", "")
                    })
            return jsonify(songs)
    except Exception as e:
        print(f"Search error: {str(e)}")  # Debug logging
        return jsonify({"error": f"Search failed: {str(e)}"})


@app.route("/stream/<video_id>")
def stream(video_id):
    try:
        print(f"Streaming video ID: {video_id}")  # Debug logging
        stream_opts = ydl_opts.copy()
        stream_opts.update({
            "format": "bestaudio/best",
            "extract_flat": False,  # We need full info for streaming
        })

        with yt_dlp.YoutubeDL(stream_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False)

            if not info or "url" not in info:
                print("No stream URL found")  # Debug logging
                return jsonify({"error": "No stream URL found"})

            return jsonify({"url": info["url"]})
    except Exception as e:
        print(f"Streaming error: {str(e)}")  # Debug logging
        return jsonify({"error": f"Streaming failed: {str(e)}"})


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
    # Use environment variable for port, defaulting to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
