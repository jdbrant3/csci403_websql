from flask import Flask, render_template, jsonify, session, request, redirect, url_for
from random import *
from flask_cors import CORS
import requests
import psycopg2 as pg 
import pandas as pd 
import pandas.io.sql as psql 
from psycopg2 import Error
import json
from datetime import datetime, timedelta
from psycopg2 import Error
from cryptography.fernet import Fernet


app = Flask(__name__,
            static_folder = "../dist/static",
            template_folder = "../dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.secret_key = b'4sJk37OyLp-yMsrncQxKF7x_wOT1cywCCPnFCIdzp9M='

@app.route('/api/query', methods=['POST'])
def execute_query():
    try:
        with open('db_conn_config.json') as config_file:
            conn_config = json.load(config_file)

        if 'username' not in session:
            return jsonify({'message': 'Not logged in'})

        else:
            session_username = session['username']
            f = Fernet(app.secret_key)
            session_password = f.decrypt(session['password']).decode("utf-8")

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
            app.logger.error(e)
            connection = None
            return jsonify({ 'message': 'Cannot fetch Query'+ query }), 401

    except (Exception, pg.OperationalError) as error :
        print ("psycopg2 error:", error)
        app.logger.error(error)
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
        # app.logger.error(error)
        print(error)
        connection = None
        return False


@app.route('/api/login', methods=['POST'])
def login():

    username = request.json['username'].strip()
    password = request.json['password'].strip()

    if not username:
        return jsonify({"message": "Missing username parameter"}), 400
    if not password:
        return jsonify({"message": "Missing password parameter"}), 400

    if authorize_login(username, password):

        if username not in session:
            f = Fernet(app.secret_key)
            encrypt_pass = f.encrypt(b'password')
            session['username'] = username
            session['password'] = encrypt_pass
            print("----SESSION CREATED----")
            print(session)
            return jsonify({'username': username, 'authorized': True})
        else:
            return jsonify({'username': username, 'authorized': True})
        # res = make_response("Setting a cookie")
        # res.set_cookie(username, username)

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