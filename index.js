const jwt = require("jsonwebtoken");
const express = require("express");
const ejs = require("ejs");
const app = express();
const bcrypt = require("bcrypt");
const session = require("express-session");
const path = require("path");

require("dotenv").config({ path: "secrets.env" });

app.set("views", __dirname + "/views");
app.set("view engine", "ejs");

app.use("/static", express.static(path.join(__dirname, "public")));
app.use(
  session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: true,
    // set max age for cookie session, currently set at 3,600,000 or 1hr
    cookie: { maxAge: 3600000 }
  })
);

// private key
const privatekey = process.env.PRIVATE_KEY;


// async function to query content from content API
const getContent = async () => {
  const clientId = process.env.CLIENT_ID;
  const clientSecret = process.env.CLIENT_SECRET;

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

// endpoint for logging in
app.get("/login", async (req, res) => {
  // check if user session is already logged in
  if(req.session.isLoggedIn){
    res.redirect("/")
  }
 
  // grab username and password from environment variable
  const envUsername = process.env.OPPKEY_VIEWER_USERNAME;
  const envPassword = process.env.OPPKEY_VIEWER_PASSWORD;

  // hash password from environment variable
  const hashedPassword = await bcrypt.hash(envPassword, 10);

  // function that denies authorization
  const reject = () => {
    res.setHeader("www-authenticate", "Basic");
    res.sendStatus(401);
  };

  // authorization constant
  const authorization = req.headers.authorization;

  // listen for authorization input
  if (!authorization) {
    return reject();
  }

  // grab authorization inputs
  const [usernameInput, passwordInput] = Buffer.from(
    authorization.replace("Basic ", ""),
    "base64"
  )
    .toString()
    .split(":");

  // if authorization inputs match username and hashed password, authenticate session and redirect to viewer
  if (
    !(
      usernameInput === envUsername &&
      (await bcrypt.compare(passwordInput, hashedPassword))
    ) == true
  ) {
    return reject();
  } else {
    req.session.isLoggedIn = true;
    res.redirect("/viewer");
  }
});

// viewer end point
app.get("/viewer", (req, res) => {
  // reject function in case of no session authorization
  const reject = () => {
    res.setHeader("www-authenticate", "Basic");
    res.sendStatus(401);
  };
  // if user session is logged in, return viewer. if not, return rejection
  if (req.session.isLoggedIn) {
    res.setHeader("Cache-Control", "no-cache, no-store, must-revalidate");
    res.setHeader("Pragma", "no-cache");
    res.setHeader("Expires", "0");
    res.render("viewer");
  } else {
    return reject();
  }
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