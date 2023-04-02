import base64
import secrets

import flask
import requests
from flask import Flask
from flask import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, send_wildcard=True)

leaderboard = {"Bob": 10, "Jimmy": 120, "Tom": 130}
leaderboardImage = {"Bob": "https://raw.githubusercontent.com/l-sheard/images/main/duckTwo.jpg", "Jimmy": "https://raw.githubusercontent.com/l-sheard/images/main/duckOne.jpg", "Tom": "https://raw.githubusercontent.com/l-sheard/images/main/duckThreeSquare.jpg"}
database = [["Bob", 10], ["Jimmy", 25], ["Tom", 110], ["Tom", 20], ["Jimmy", 95]]
users = {"Bob": "pass", "Jimmy": "pass2"}
userStatus = {"Bob": "happy", "Jimmy": "sad", "Tom": "dead"}
#dead, dying, sad, happy
userCredits = {"Bob": 25, "Jimmy": 15, "Tom": 9}
tokens = {}

PROMPT = """Given data about a product listed on Amazon, convert the data into a machine readable format. The input is a JSON object containing the following fields:
- name: the title of the product as a string (this may be very verbose)
- model: the model of the product as a string, if listed by the seller
- manufacturer: the manufacturer of the product as a string, if listed by the seller (this may be incorrect)
- categoryName: the category of the product as categorised in the Amazon website (this may be incorrect)
The response must be purely in a JSON format. There must be no explanation whatsoever. The only permitted keys in the response are conciseName, correctedManufacturer, and category. The conciseName must be a string concisely but accurately representing the title of the product. This will be fuzzy matched against a database of products. The correctedManufacturer must be a string representing the entity or organisation that manufactured the product. The category must represent the type of item that is being purchased. No keys of the response are optional, and a best guess must be provided if an answer cannot be provided accurately. All fields must be plaintext with no special characters (except whitespace).
Example input: {"name": "Apple iPhone 14 (128 GB) - BlueApple iPhone 14 (128 GB) - Blue", "model": "IPhone 14", "manufacturer": "Apple iPhone", "categoryName": "allProducts"}
Example output: {"name": "iPhone 14", "manufacturer": "Apple", "category": "Phones"}
Input: """

@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'

@app.route('/api/v1/subtractDuckCredits', methods = ['GET'])
def subtractDuckCredits():
    # Subtracts the amount spent in the duck store from the users credits total
    amountSpent = request.args.get('amountSpent').strip()
    token = request.args.get('token').strip()
    if token in tokens:
        username = tokens[token]
        userCredits[username] = userCredits[username] - amountSpent
    else:
        return {}, 403, {}

@app.route('/api/v1/getDuckCredits', methods = ['GET'])
def getDuckCredits():
    # returns the number of credits that the user has
    token = request.args.get('token').strip().encode("utf-8")
    print(token, tokens)
    if token in tokens:
        username = tokens[token]
        return {"userCredits": userCredits[username]}
    else:
        return {}, 403, {}

@app.route('/api/v1/getUserStatus', methods = ['GET'])
def getStatus():
    username = request.args.get('username').strip()
    if username in userStatus:
        return {"userStatus": userStatus[username]}
    else:
        return {}, 403, {}

@app.route('/api/v1/getCarbon', methods = ['GET'])
def getCarbon():
    name = request.args.get('name').strip()
    manufacturer = request.args.get('manufacturer').strip()
    #model = request.args.get('model').strip()
    categoryName = request.args.get('categoryName').strip()
    price_cents = request.args.get('price_cents').strip()
    price_currency = request.args.get('price_currency').strip()
    #completion = openai.Completion.create(
    #    model="text-davinci-003",
    #    prompt=PROMPT + json.dumps({"name": name, "manufacturer": manufacturer, "model": model, "categoryName": categoryName}) + "\nOutput:",
    #    stop="}"
    #)
    #for choice in completion.choices:
    #    print(choice.message)
    #    try:
    #        fixed = json.loads(choice.message) + "}"
    #        name = fixed["conciseName"]
    #        manufacturer = fixed["manufacturer"]
    #        categoryName = fixed["category"]
    #        print("used gpt", fixed)
    #        break
    #    except (ValueError, TypeError, SyntaxError) as e:
    #        print("gpt failed", e)
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
    response = requests.get(url, headers=headers).json()
    if "kgco2" not in response:
        return {"carbon": None}, {
        "Access-Control-Allow-Origin": "*"
    }
    return {"carbon": round(response["kgco2"], 2)}, {
        "Access-Control-Allow-Origin": "*"
    }

@app.route('/api/v1/saveToLeaderboard', methods = ['GET'])
def saveToLeaderboard():
    token = request.args.get('token').strip().encode("utf-8")
    username = tokens[token]
    carbonForOrder = request.args.get('carbonForOrder').strip()
    if username in leaderboard:
        leaderboard[username] = leaderboard[username] + int(carbonForOrder)
    else:
        leaderboard[username] = carbonForOrder

    database.append([username, carbonForOrder])
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
        imageURL = leaderboardImage[key]
        leaderboardNew.append({"username": username, "total": total, "url": imageURL})
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
            token = base64.urlsafe_b64encode(secrets.token_bytes())
            resp.data = token
            tokens[token] = username
        else:
            print("sad")
            resp.data = "sad"
    else:
        print("sad")
        resp.data = "sad"

    return resp


