from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
import requests, os, jwt, time
import google.generativeai as genai

app = FastAPI()

# ===== ENV =====
CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
JWT_SECRET = os.environ["JWT_SECRET"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

REDIRECT_URI = "https://YOUR-BACKEND.onrender.com/auth/callback"
FRONTEND_URL = "https://xyro123-zeppfusion.hf.space"

# ===== LOGIN =====
@app.get("/login")
def login():
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
    )
    return RedirectResponse(url)

# ===== CALLBACK =====
@app.get("/auth/callback")
def callback(code: str):
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    ).json()

    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {token_res['access_token']}"},
    ).json()

    jwt_token = jwt.encode(
        {
            "email": userinfo["email"],
            "name": userinfo["name"],
            "exp": time.time() + 86400
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    return RedirectResponse(f"{FRONTEND_URL}/?token={jwt_token}")

# ===== CHAT API =====
@app.post("/chat")
def chat(data: dict, token: str):
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    res = model.generate_content(data["message"])

    return {
        "user": payload["email"],
        "reply": res.text
    }
