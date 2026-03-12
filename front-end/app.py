from flask import Flask, render_template, send_from_directory
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/static")

API_URL = os.getenv("API_URL")

if not API_URL:
    raise RuntimeError("API_URL não definida nas variáveis de ambiente.")

@app.route('/')
def index():
    return render_template('index.html', api_url = API_URL)

@app.route('/<path:path>')
def catch_all(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return index()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)