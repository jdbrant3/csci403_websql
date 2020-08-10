from flask import Flask, render_template, jsonify, session, request
from random import *
from flask_cors import CORS
import requests
import psycopg2 as pg 
import pandas as pd 
import pandas.io.sql as psql 
from tabulate import tabulate
from psycopg2 import Error
import json
import jwt
from datetime import datetime, timedelta
from psycopg2 import Error
from cryptography.fernet import Fernet
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, JWTManager
from pydantic import BaseModel

app = Flask(__name__,
            static_folder = "../dist/static",
            template_folder = "../dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.secret_key = b'YOUR_SECRET_KEY'

@app.route('/api/query', methods=['POST'])
def execute_query():
    try:
        with open('db_conn_config.json') as config_file:
            conn_config = json.load(config_file)


        connection = pg.connect(user = session_username,
                                password = session_password,
                                host = conn_config['host'],
                                port = conn_config['port'],
                                database = conn_config['dbname'])

        connection.autocommit = True
        cursor = connection.cursor()

    
        try:
            query = request.json['query'].lstrip()

            if query.lower()[0:5] == 'show ' or query.lower()[0:7] == 'select ':
                table = pd.read_sql(query, connection)
                response = table.to_json(orient='records')
                return response
            else:
                cursor.execute(query)
                return json.dumps({ 'result' : 'success' })

        except pg.OperationalError as e:
            print('Unable to connect!\n{0}').format(e)
            connection = None
            return jsonify({ 'message': 'Cannot fetch Query'+ query }), 401

    except (Exception, pg.OperationalError) as error :
        print ("psycopg2 error:", error)
        return jsonify({ 'message': 'Connection Failed' }), 401
    finally:
        #closing database connection.
            connection = None
            if(connection):
                cursor.close()
                connection.close()



def authorize_login(username, password):
    try:
        with open('db_conn_config.json') as config_file:
            conn_config = json.load(config_file)


        connection = pg.connect(user = username,
                                password = password,
                                host = conn_config['host'],
                                port = conn_config['port'],
                                database = conn_config['dbname'])
        if(connection):
            return True

    except (Exception, pg.Error) as error :
        connection = None
        return False


@app.route('/api/login', methods=['POST'])
def login():
    username = request.json['username'].strip()
    password = request.json['password'].strip()
    nickname = request.json['username'].strip()

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if authorize_login(username, password):

        f = Fernet(app.secret_key)
        encrypt_pass = f.encrypt(b'password')
        session[username] = [username, encrypt_pass, datetime.utcnow()]
        print("Session Created:", session[username])

        res = make_response("Setting a cookie")
        res.set_cookie(username, username)
            
        return jsonify({'username': session["USERNAME"], 'authorized': True})
    else:
        return jsonify({'username': username, 'authorized': False})


# @app.route("/api/logout", methods=["POST"])
# def logout():
#     token = request.form.get("token")
#     status = authModel.blacklist(token)
#     return {'success': status}


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")