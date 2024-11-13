from flask import Flask, render_template, request, session
import jwt
import os
from dotenv import load_dotenv
import requests
import base64
from config import Config
import json 

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
    session["ricoh_cloud_token"] = ricoh_cloud_access_token
    return ricoh_cloud_access_token


# Function to query content from the RICOH360 API
def get_content():
    get_token_for_cloud_content()
    cloud_content_token = session["ricoh_cloud_token"]
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


@app.route("/livingroom")
def stage():
    content_id = request.args.get('contentId')
    viewer_token = request.args.get('viewerToken')
    cloud_token = session["ricoh_cloud_token"]

    # print(f"cloud token: {cloud_token}")
    content_headers = {"Authorization": f"Bearer {cloud_token}"}
    content_response = requests.get(
        f"https://api.ricoh360.com/contents/{content_id}/staging:type_living_room", headers=content_headers
    )
    response_dict = content_response.json()
    first_content_id = response_dict["results"][0]["content_id"]
    print(f"first content ID: {first_content_id}")
    print(json.dumps(response_dict, indent=4, sort_keys=True))
    return render_template("single_image.html",
                           token=viewer_token,
                           contentId=first_content_id,
                           )


if __name__ == "__main__":
    app.config.from_object(Config)
    app.run(port=3000, debug=True)
    print("Open browser at http://localhost:3000 or http://127.0.0.1:3000")
