const jwt = require("jsonwebtoken");
const express = require("express");
const app = express();
const path = require("path");

require("dotenv").config({ path: "secrets.env" });

app.set("views", __dirname + "/views");
app.set("view engine", "ejs");
app.use("/static", express.static(path.join(__dirname, "public")));

/**
 * You will need three things from RICOH.
 * 1. private key for the RICOH Viewer
 * 2. Client ID to store/retrieve images and for transformations
 * 3. Client Secret
 */
const privatekey = process.env.PRIVATE_KEY;
const clientId = process.env.CLIENT_ID;
const clientSecret = process.env.CLIENT_SECRET;

/**
 * async function to query content such as images
 * from RICOH360 platform API
 * @returns list of content with content ID needed by viewer
 */
const getContent = async () => {
  // post to aws auth to get authentication token
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

  // use token authentication from AWS to fetch content from content API
  const res = await fetch("https://api.ricoh360.com/contents?limit=50", {
    method: "GET",
    headers: {
      Authorization: "Bearer " + tokenObject.access_token,
    },
  });
  const data = await res.json();
  return data;
};

// create token for viewer API with JWT
const createToken = () => {
  const payload = {
    // Get client id for platform API from environmental variable
    client_id: process.env.CLIENT_ID
  };

  const accessToken = jwt.sign(payload, privatekey, {
    algorithm: "RS256",
    expiresIn: "60m",
  });

  return accessToken;
};

// endpoint for front end to get a accesstoken with createToken function
app.get("/token", (req, res) => {
  let token = createToken();
  res.status(200).send(token);
});

// endpoint for front end to access content with getContent function
app.get("/content", async (req, res) => {
  let test = await getContent();
  res.status(200).send(test);
});

// viewer end point
app.get("/viewer", (req, res) => {
  res.render("viewer");
});

// endpoint for home page
app.get("/", (req, res) => {
  res.render("index");
});

// endpoint for logging out
app.get("/logout", (req, res) => {
  req.session.destroy(() => {
    res.redirect("/");
  });
});

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});