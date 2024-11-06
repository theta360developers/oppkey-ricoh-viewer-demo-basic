from flask import Flask, render_template
import os
import requests
import jwt
from dotenv import load_dotenv
import base64

load_dotenv("secrets.env")

app = Flask(__name__)
app.template_folder = "views"
app.static_folder = "public"

# Retrieve environment variables
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


# Function to query content from the RICOH360 API
def get_content():
    # Endpoint and authentication for AWS token
    token_endpoint = "https://saas-prod.auth.us-west-2.amazoncognito.com/oauth2/token"  # noqa: E501
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode("utf-8")  # noqa: E501
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth}",
    }
    body = {"grant_type": "client_credentials", "scope": "all/read"}

    # Request AWS token
    token_response = requests.post(token_endpoint, headers=headers, data=body)
    token_object = token_response.json()
    access_token = token_object.get("access_token")

    # Fetch content using the token
    content_headers = {"Authorization": f"Bearer {access_token}"}
    content_response = requests.get(
        "https://api.ricoh360.com/contents?limit=50", headers=content_headers
    )
    content_data = content_response.json()
    return content_data


# Function to create a JWT token for the viewer API
def create_token():
    payload = {"client_id": CLIENT_ID}
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    # Decode to UTF-8 if necessary

    return token if isinstance(token, str) else token.decode("utf-8")


# Route for the homepage with viewer
# inspect views/flask_viewer.html for information on how to use the viewer.
@app.route("/")
def index():
    """Send token and data to web page
    token is created from the JWT Python package (see requirements.txt for module info)
    You need a Private Key from RICOH in order to sign the token and use it with the
    RICOH360 Viewer.

    The token is sent to views/flask_viewer.html along with the data
    about the THETA images stored in the RICOH360 Cloud
    """
    token = create_token()
    content_data = get_content()
    return render_template("flask_viewer.html", token=token, content_data=content_data)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
    print("Open browser at http://localhost:3000 or http://127.0.0.1:3000")
