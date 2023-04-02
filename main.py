import base64
import secrets

import flask
from flask import Flask
import requests
from flask import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

leaderboard = {"Bob": 0, "Jimmy": 0}
users = {"user": "pass", "user2": "pass2"}

@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'

@app.route('/api/v1/getCarbon', methods = ['GET'])
def getCarbon():
    name = request.args.get('name').strip()
    manufacturer = request.args.get('manufacturer').strip()
    categoryName = request.args.get('categoryName').strip()
    price_cents = request.args.get('price_cents').strip()
    price_currency = request.args.get('price_currency').strip()
    url = "https://api.ditchcarbon.com/v1.0/product?name=" + name + "&manufacturer=" + manufacturer
    if categoryName is not None:
        url = url + "&category_name=" + categoryName
    if price_cents is not None:
        url = url + "&price_cents=" + price_cents
    if price_currency is not None:
        url = url + "&price_currency=" + price_currency

    headers = {
        "accept": "application/json",
        "authorization": "Bearer cb527966a16b153262e8b32fdfe809d0"
    }
    response = requests.get(url, headers=headers)
    return {"carbon": response.json()["kgco2"]}, {
        "Access-Control-Allow-Origin": "*"
    }

@app.route('/api/v1/saveToLeaderboard', methods = ['GET'])
def saveToLeaderboard():
    username = request.args.get('username').strip()
    carbonForOrder = request.args.get('carbonForOrder').strip()
    if username in leaderboard:
        leaderboard[username] = leaderboard[username] + int(carbonForOrder)
    else:
        leaderboard[username] = carbonForOrder

    leaderboardNew = []
    for key in leaderboard:
        username = key
        total = leaderboard[key]
        leaderboardNew.append({"username": username, "total": total})
    leaderboardNew = sorted(leaderboardNew, key=lambda x: x["total"])
    return {"leaderboard": leaderboardNew}

@app.route('/api/v1/getLeaderboard', methods = ['GET'])
def getLeaderboard():
    leaderboardNew = []
    for key in leaderboard:
        username = key
        total = leaderboard[key]
        leaderboardNew.append({"username": username, "total": total})
    leaderboardNew = sorted(leaderboardNew, key=lambda x: x["total"])
    return leaderboardNew, {
        "Access-Control-Allow-Origin": "*"
    }


@app.route('/api/v1/verifyLogin', methods = ['GET'])
def verifyLogin():
    username = request.args.get('username').strip()
    password = request.args.get('password').strip()

    resp = flask.Response()
    resp.headers["Access-Control-Allow-Origin"] = "*"
    if username in users:
        if users[username] == password:
            print("logged in")
            resp.data = base64.b64encode(secrets.token_bytes())
        else:
            print("sad")
            resp.data = "sad"
    else:
        print("sad")
        resp.data = "sad"

    return resp


