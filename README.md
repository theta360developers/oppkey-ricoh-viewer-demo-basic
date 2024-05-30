# RICOH360 Viewer API Demo

## Live site: [https://r360.oppget.com/](https://r360.oppget.com/)

![login screen](readme_assets/login_screen.png)

Contact Oppkey for login to public cloud-based site. Refer to code on GitHub
repository [oppkey-ricoh360-viewer-demo-with-login](https://github.com/codetricity/oppkey-ricoh360-viewer-demo-with-login) for an example showing how to deploy to Vercel with basic authentication
login.

## Features


### Split Screen and Image Enhancement

Pre-built split screen component shown using RICOH's included
image enhancement technology. 

![split screen](readme_assets/split_screen.png)

### Annotation

![annotate menu](readme_assets/annotate_menu.png)

Written notes and simple drawings appear in viewer.

![annotate](readme_assets/annotate.png)


## Demo Overview

![Demo Overview](readme_assets/slides/01_overview.png)

The demo is intended to be a live hosted site on AWS or Vercel.
It consists of a backend server and a front end web application.
The server can be run on a laptop with node.

---

![process steps](readme_assets/slides/02_process.png)

---

![step 1: go to business web app](readme_assets/slides/03_step_1.png)

### running demo locally on a laptop or computer

Prior to running locally, you will need obtain a client id, client secret,
and private key from RICOH and set the information in `secrets.env`.
Oppkey can assist partners in the setup.  If the `secrets.env` file
is not set up properly, the application will fail to run.  

Full `secrets.env` used by Oppkey is available [here](https://github.com/codetricity/oppkey-ricoh-viewer-credentials/blob/main/README.md). The
private key, client id, and client secret are in a private GitHub repo. If you are a RICOH staff or partner and have authorization to use the Oppkey client id, private key, and client secret, then contact Oppkey and we will send you the file. Otherwise, you will need to use your own keys that you got from RICOH.

RICOH Viewer API with Node.js/Express.js & EJS templating

1. [Project Structure](#project-structure)
2. [Getting the app running](#getting-the-app-running)
3. [How It Works](#how-it-works)
4. [Environment Variables](#environment-variables)

## Project Structure

- **ricoh-viewer_testing**: The main project directory
  - **views/**: Folder that holds view/HTML files (EJS markdown files)
    - **index.ejs**: Home/landing page template
    - **viewer.ejs**: Viewer page template
  - **index.js**: File where server side functions and API endpoints to these functions are held

## Getting the app running

1. Install Node.js : https://nodejs.org/en - Note that Oppkey uses [nvm](https://github.com/nvm-sh/nvm) to manage node versions.  However, it may be simpler for you to install node straight from the node site.
2. In a new terminal in the root directory of the project, run `npm install`
3. Run `npm run start`, the app should start locally on port 3000, `http://localhost:3000`


## How it Works

- [RICOH Partner Technical Documentation Site](https://docs.ricoh360.com/partners/) - requires login

![docs overview](readme_assets/docs_overview.png)

### Server-side functions

#### createToken()

```typescript
const privatekey = `-----BEGIN PRIVATE KEY-----
  <client private key>
-----END PRIVATE KEY-----`;

const createToken = () => {
  const payload = {
    client_id: <your client id>,
  };

  const accessToken = jwt.sign(payload, privatekey, {
    algorithm: "RS256",
    expiresIn: "60m",
  });

  return accessToken;
};
```

- `createToken()` uses a payload object with your clientID and optionally your groupID
- Using [jsonwebtoken package](https://www.npmjs.com/package/jsonwebtoken), you create and return an access token with an encryption algorithm that expires in a certain time (60 minutes)
- This function will be called client side via the API endpoint for this function and used in a callback function for Ricoh's viewer API

#### getContent()

```typescript
const clientId = "<your client id>";
const clientSecret = "<your client secret>";

const getContent = async () => {
  const tokenEndpoint =
    "https://saas-prod.auth.us-west-2.amazoncognito.com/oauth2/token";

  const auth = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");

  const requestData = {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      Authorization: `Basic ${auth}`,
    },
    body: new URLSearchParams({
      grant_type: "client_credentials",
      scope: "all/read",
    }),
  };

  const tokenResponse = await fetch(tokenEndpoint, requestData);
  const tokenObject = await tokenResponse.json();

  const res = await fetch("https://api.ricoh360.com/contents?limit=3", {
    method: "GET",
    headers: {
      Authorization: "Bearer " + tokenObject.access_token,
    },
  });
  const data = await res.json();

  return data;
};
```

- This function takes your clientID and clientSecret, turns it into base64 string format and sends a post request to https://saas-prod.auth.us-west-2.amazoncognito.com/oauth2/token (set as tokenEndpoint) to get a token to use for Ricoh content API
- After getting the token response, it creates another post request to Ricoh content API with the token as authorization and returning the data

### Server-side endpoints

#### /

```
app.get("/", (req, res) => {
  res.render("index");
});
```

This endpoint returns the EJS template file (index.ejs) in ./views


#### /viewer

```typescript
app.get("/viewer", (req, res) => {
  res.render("viewer");
});
```
Calls up the main viewer with the split view, transformations, and
content.

#### /token

```typescript
app.get("/token", (req, res) => {
  let token = createToken();
  res.status(200).send(token);
});
```

This endpoint calls on the createToken() server-side function and returns the token

#### /content

```javascript
app.get("/content", async (req, res) => {
  let test = await getContent();
  res.status(200).send(test);
});
```

This endpoint calls on the getContent() async function and returns the content data which is needed by the viewer.

### Client-side (in ./views/index.ejs)

#### fetchContent

```typescript
const fetchContent = async () => {

  // fetch content from /content endpoint and store data in const data
  const res = await fetch("/content", {
    method: "GET",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  const data = await res.json();

  // populate buttons on left pane list
  const leftList = document.getElementById("leftList");
  for (let i = 0; i < data.length; i++) {
    if (data[i].status === "uploaded") {
      console.log(data[i]);
      const listItem = document.createElement("li");
      listItem.innerHTML = `<div>
        <img src="${
          data[i].thumbnail_url
        }" onclick="viewer.switchScene({ contentId: '${
        data[i].content_id
      }'},${0})">
        <button type="button" onclick="viewer.switchScene({ contentId: '${
          data[i].content_id
        }',transform:'enhancement'},${0})">
          Enhance
        </button>
        <button type="button" onclick="viewer.switchScene({ contentId: '${
          data[i].content_id
        }',transform:'b_person'},${0})">
          Blur People
        </button>
        <button type="button" onclick="viewer.switchScene({ contentId: '${
          data[i].content_id
        }',transform:'p_cubic'},${0})">
          Cubic View
        </button>
      </div>`;
      leftList.append(listItem);
    }
  }

  // populate buttons on right pane list
  const rightList = document.getElementById("rightList");
  for (let i = 0; i < data.length; i++) {
    if (data[i].status === "uploaded") {
      console.log(data[i]);
      const listItem = document.createElement("li");
      listItem.innerHTML = `<div>
        <img src="${
          data[i].thumbnail_url
        }" onclick="viewer.switchScene({ contentId: '${
        data[i].content_id
      }'},${1})">
        <button type="button" onclick="viewer.switchScene({ contentId: '${
          data[i].content_id
        }',transform:'enhancement'},${1})">
          Enhance
        </button>
        <button type="button" onclick="viewer.switchScene({ contentId: '${
          data[i].content_id
        }',transform:'b_person'},${1})">
          Blur People
        </button>
        <button type="button" onclick="viewer.switchScene({ contentId: '${
          data[i].content_id
        }',transform:'p_cubic'},${1})">
          Cubic View
        </button>
      </div>`;
      rightList.append(listItem);
    }
  }
};
```

`fetchContent()` makes a async get request to the backend endpoint /content and returns content data and populates listing of images with transform buttons

#### fetchToken()

```javascript
const fetchToken = async () => {
  const res = await fetch("/token", {
    method: "GET",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  const data = await res.text();
  return data;
};
```

`fetchToken()` makes a async get request to the backend endpoint /token and returns a token

#### ui

```typescript
const ui = {
  cropping: {
    horizontalMargin: 15,
    verticalMargin: 75,
  },
  toolbar: {
    isHidden: false,
    cancelButton: {
      label: "Cancel",
    },
    checkButton: {
      label: "Done",
    },
    autoRotateButton: {
      isHidden: false,
      label: "Auto Rotate",
    },
    croppingButton: {
      isHidden: false,
      enterLabel: "Enter Cropping",
      exitLabel: "Exit Cropping",
    },
    drawingButton: {
      isHidden: false,
      enterLabel: "Enter Drawing",
      exitLabel: "Exit Drawing",
    },
    fullScreenButton: {
      isHidden: false,
      enterLabel: "Enter Full Screen",
      exitLabel: "Exit Full Screen",
    },
    homePositionButton: {
      isHidden: false,
      label: "Home Position",
    },
    liveStreamingControlButtons: {
      isHidden: false,
      startLabel: "Start Streaming",
      stopLabel: "Stop Streaming",
      speakerOnLabel: "Speaker On",
      speakerOffLabel: "Speaker Off",
    },
    zoomControlButtons: {
      isHidden: false,
      zoomInLabel: "Zoom In",
      zoomOutLabel: "Zoom Out",
    },
  },
  tooltip: {
    isHidden: false,
  },
  verticalPanel: {
    isHidden: false,
    topMargin: 25,
  },
};
```

- Const ui is a parameter that is passed into the viewer object
- Allows definition and hiding/showing of ui buttons and functionalities

#### onCropped

```typescript
const onCropped = async (url) => {
  const image = await fetch(url);
  const imageBlob = await image.blob();
  const imageURL = URL.createObjectURL(imageBlob);
  const downloadLink = document.createElement('a');
  downloadLink.href = imageURL;
  downloadLink.download = 'cropped_image.jpeg';
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
};
```

In the viewer, there is a crop function, that crop function passes in the cropped image URL to this callback function and downloads the cropped image to your computer.

#### viewer

```typescript
const viewer = new RICOH360Viewer({
  divId: "viewer",
  onFetchToken: fetchToken,
  isCubemapEnabled: true,
  ui,
  onSelected: (index) => {
    console.log("selected", index);
  },
});

viewer.start({
  contentId: "6b004f76-60cf-4f14-ae3c-49b7dee4aca2",
  transform: "enhancement",
});
```
- Viewer is Ricoh embedded viewer API
- Viewer is initialized by specific a divId to inject the viewer UI into, an onFetchToken function for authorization and a CubeMapEnabled
- Viewer is started with a contentID (call fetchContent() function to get contentIDs) and a transform value ie. "enhancement" or "undefined"

## Environment Variables

Create a `secrets.env` file in the root of the project with the following secrets:

```text
CLIENT_ID=<Your unique client id from RICOH for the platform API>
CLIENT_SECRET=<client secret for your client id for the platform API>
PRIVATE_KEY="<long private key for the viewer>"
```

## Deploy Your Own Demo on Vercel

Please refer to the project [oppkey-ricoh360-viewer-demo-with-login](https://github.com/codetricity/oppkey-ricoh360-viewer-demo-with-login)
 for a variation of this project with:

* `vercel.json` file
* local login example to secure your public site

