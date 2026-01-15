from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import requests
import os

app = FastAPI()

CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "https://your-backend.onrender.com/auth/callback"

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

    # 👉 энд JWT үүсгээд frontend рүү буцаана
    return userinfo

