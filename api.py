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

# from app.models import Users

app = Flask(__name__,
            static_folder = "../dist/static",
            template_folder = "../dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# jwt = JWTManager(app)
# app.config["JWT_SECRET_KEY"] = "naturally Hans is wet, he is standing under a waterfall"
AUTHSECRET = "naturally Hans is wet, he is standing under a waterfall"


@app.route('/api/query', methods=['POST'])
def execute_query():
    try:
        with open('db_conn_config.json') as config_file:
            conn_config = json.load(config_file)

        connection = pg.connect(user = 'jdbrant',
                                password = 'jimmy123',
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
            # app.logger.error(e)
            return jsonify({ 'message': 'Cannot fetch Query'+ query }), 401

    except (Exception, pg.OperationalError) as error :
        print ("psycopg2 error:", error)
        # app.logger.exception(error)
        # connection = None
        return jsonify({ 'message': 'Connection Failed' }), 401
    finally:
        #closing database connection.
            connection = None
            if(connection):
                cursor.close()
                connection.close()
                # print("PostgreSQL connection is closed")


@app.route('/api/auth', methods=["POST"])
def auth():
    try:
        with open('db_conn_config.json') as config_file:
            conn_config = json.load(config_file)

        client_username = request.json["username"]
        client_password = request.json["password"]

        connection = pg.connect(user = client_username,
                                password = client_password,
                                host = conn_config['host'],
                                port = conn_config['port'],
                                database = conn_config['dbname'])

    except (Exception, pg.Error) as error :
        return jsonify({ 'message': 'Login Failed', 'authenticated': False }), 401
        
    finally:
        #closing database connection.
            if(connection):
                connection.close()
                token = jwt.encode({
                    'sub': client_username,
                    'iat': datetime.utcnow(),
                    'exp': datetime.utcnow() + timedelta(minutes=30)},
                    AUTHSECRET)
                return jsonify({'token': token.decode('UTF-8') })


# @app.route('/api/login', methods=['POST'])
# def login():
#     username = request.json['username']
#     password = request.json['password']

#     if not username:
#         return jsonify({"msg": "Missing username parameter"}), 400
#     if not password:
#         return jsonify({"msg": "Missing password parameter"}), 400

#     # user = Users(username, password)

#     # if user is None:
#         # return jsonify({'success': False, 'message': 'Bad username or password'}), 401

#     access_token = create_access_token(identity=username)
#     app.logger.info("Access Token:", access_token)
#     return jsonify({'success': True, 'token': access_token}), 200


# @app.route('/api/verify-token', methods=['POST'])
# @jwt_required
# def verify_token():
#     return jsonify({success: True}), 200


# @app.route('/api/protected', methods=['GET'])
# @jwt_required
# def protected():
#     current_user = get_jwt_identity()
#     return jsonify(logged_in_as=current_user), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    token = request.form.get("token")
    status = authModel.blacklist(token)
    return {'success': status}


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")