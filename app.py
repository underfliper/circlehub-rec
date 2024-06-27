import json
import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, abort, request, Response

from models.suggest_posts import suggest_posts
from models.check_spam import check_comment
from models.suggest_follows import suggest_follows


load_dotenv()
app = Flask(__name__)



@app.get("/suggestedposts/<int:user_id>")
def get_suggested_posts(user_id):
    url = os.getenv("DATABASE_URL")
    connection = psycopg2.connect(url)

    return suggest_posts(connection, user_id)


@app.get("/suggestedfollows/<int:user_id>")
def get_suggested_follows(user_id):
    url = os.getenv("DATABASE_URL")
    connection = psycopg2.connect(url)

    return suggest_follows(connection, user_id)


@app.post("/checkspam")
def check_spam():
    url = os.getenv("DATABASE_URL")
    connection = psycopg2.connect(url)

    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):
        data = request.json

        if ('text' in data):
            if (isinstance(data['text'], str)):
                return check_comment(data['text'])
            else:
                res = Response(
                    json.dumps({"message": "Wrong data!", "code": 400, "status": "FAIL"}),
                    mimetype="application/json",
                    status=400)
                return abort(res)
        else:
            res = Response(
                json.dumps({"message": "Wrong data!", "code": 400, "status": "FAIL"}),
                mimetype="application/json",
                status=400)
            return abort(res)
        
    else:
        res = Response(
            json.dumps({"message": "Content-Type not supported!", "code": 400, "status": "FAIL"}),
            mimetype="application/json",
            status=400)
        return abort(res)