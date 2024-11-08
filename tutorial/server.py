from flask import Flask, render_template
import jwt
import os
from dotenv import load_dotenv

load_dotenv("secrets.env")

app = Flask(__name__)
app.template_folder = "views"
app.static_folder = "public"

# Retrieve environment variables
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def create_token():
    payload = {"client_id": CLIENT_ID}
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    # Decode to UTF-8 if necessary

    return token if isinstance(token, str) else token.decode("utf-8")


@app.route("/")
def index():
    token = create_token()
    return render_template("index.html",  token=token)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
    print("Open browser at http://localhost:3000 or http://127.0.0.1:3000")
