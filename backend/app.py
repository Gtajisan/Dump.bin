from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os, uuid, json
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = "pastes"
SHORTLINK_FILE = "shortlinks.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
shortlinks = json.load(open(SHORTLINK_FILE, "r")) if os.path.exists(SHORTLINK_FILE) else {}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" in request.files:
        file = request.files["file"]
        ext = Path(file.filename).suffix
        paste_id = uuid.uuid4().hex[:6] + ext
        file.save(os.path.join(UPLOAD_FOLDER, secure_filename(paste_id)))
        return url_for("view_paste", paste_id=paste_id, _external=True), 200
    elif "short" in request.form:
        short_url = request.form["short"]
        key = uuid.uuid4().hex[:6]
        shortlinks[key] = short_url
        json.dump(shortlinks, open(SHORTLINK_FILE, "w"))
        return url_for("redirect_short", key=key, _external=True), 200
    return "No valid data provided", 400

@app.route("/p/<paste_id>", methods=["GET"])
def view_paste(paste_id):
    path = os.path.join(UPLOAD_FOLDER, paste_id)
    if not os.path.exists(path):
        return "Paste not found", 404
    with open(path, "r") as f:
        content = f.read()
    ext = Path(paste_id).suffix.lstrip(".")
    return render_template("paste.html", content=content, ext=ext)

@app.route("/s/<key>")
def redirect_short(key):
    return redirect(shortlinks.get(key, "/"))

@app.route("/raw/<paste_id>")
def raw_paste(paste_id):
    return send_from_directory(UPLOAD_FOLDER, paste_id)

if __name__ == "__main__":
    app.run(debug=True)
  
