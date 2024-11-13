from flask import Flask, render_template, g
import jwt
import os
from dotenv import load_dotenv
import requests
import base64


load_dotenv("secrets.env")

app = Flask(__name__)
app.template_folder = "."

# Retrieve environment variables
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def create_token():
    payload = {"client_id": CLIENT_ID}
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    # Decode to UTF-8 if necessary

    return token if isinstance(token, str) else token.decode("utf-8")


def get_token_for_cloud_content():
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
    ricoh_cloud_access_token = token_object.get("access_token")
    g.ricoh_cloud_token = ricoh_cloud_access_token
    return ricoh_cloud_access_token


# Function to query content from the RICOH360 API
def get_content():
    get_token_for_cloud_content()
    cloud_content_token = g.get("ricoh_cloud_token")
    # Fetch content using the token
    content_headers = {"Authorization": f"Bearer {cloud_content_token}"}
    content_response = requests.get(
        "https://api.ricoh360.com/contents?limit=40", headers=content_headers
    )
    content_data = content_response.json()
    return content_data


@app.route("/")
def index():
    token = create_token()
    content_data = get_content()
    thumburls = []

    contentIds = []
    for single_content in content_data:
        if ("thumbnail_url" in single_content):
            contentIds.append(single_content["content_id"])
            thumburls.append(single_content["thumbnail_url"])
    return render_template("index.html",
                           token=token,
                           contentIds=contentIds,
                           thumburls=thumburls
                           )


@app.route("/stage/<content_id>")
def stage(content_id):
    viewer_token = create_token()
    cloud_token = g.get("ricoh_cloud_token")

    print(f"token: {cloud_token}")
    return render_template("single_image.html",
                           token=viewer_token,
                           contentId=content_id,
                           )


if __name__ == "__main__":
    app.run(port=3000, debug=True)
    print("Open browser at http://localhost:3000 or http://127.0.0.1:3000")