import json
import re
from datetime import datetime, timedelta
from random import *

import pandas as pd
import pandas.io.sql as psql
import psycopg2 as pg
import requests
from cryptography.fernet import Fernet
from flask import (
    Flask, jsonify, redirect, render_template, request, session, url_for)
from flask_cors import CORS, cross_origin
from psycopg2 import Error

app = Flask(__name__,
            static_folder = "../dist/static",
            template_folder = "../dist")
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app, resources={r"/api/*": {'origins': ['http://localhost:8080', 'http://127.0,0,1:8000']}}, headers=['Content-Type'], expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True)

app.secret_key = b'4sJk37OyLp-yMsrncQxKF7x_wOT1cywCCPnFCIdzp9M='

def parse(query_string):
    multiline_comment = re.compile(r'(\s*/\*.*?\*/)', flags = re.MULTILINE|re.DOTALL)
    single_line_comment = re.compile(r'(\s*--.*$)', flags = re.MULTILINE)

    # let ; terminate each query (assume comments go only with following queries)
    queries = query_string.split(';')

    result = []

    for q in queries:
        comment = ''
        while True:

            match = multiline_comment.match(q)
            if match:
                comment = comment + match.group(0)
                q = q[match.end():]
                continue

            match = single_line_comment.match(q)
            if match:
                comment = comment + match.group(0)
                q = q[match.end():]
                continue

            # if we found no leading comments, assume the rest is query
            break

        result.append((q.strip(), comment.strip()))

    return result


@app.route('/api/query', methods=['POST'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def execute_query():
    try:
        with open('db_conn_config.json') as config_file:
            conn_config = json.load(config_file)

        if 'username' not in session:
            return jsonify({'message': 'Not logged in'})

        else:
            session_username = session['username']
            f = Fernet(app.secret_key)
            session_password = f.decrypt(session['password']).decode('utf-8')

        connection = pg.connect(user = session_username,
                                password = session_password,
                                host = conn_config['host'],
                                port = conn_config['port'],
                                database = conn_config['dbname'])

        connection.autocommit = True
        cursor = connection.cursor()

    
        queries = parse(request.json['query'])
        results = []

        for (query, comment) in queries:
            if query == '':
                if len(comment) > 0:
                    results.append({ 'comment' : comment })
            elif query.lower()[0:5] == 'show ' or query.lower()[0:7] == 'select ':
                query = query + ';'
                try:
                    cursor.execute(query)
                    rowcount = cursor.rowcount

                    # should make this a settable limit on the client side at some point
                    limit_message = ''
                    if (rowcount > 500):
                        data = cursor.fetchmany(500)
                        limit_message = 'Query resulted in ' + str(rowcount) + ' rows, exceeding limit.  First 500 rows displayed above.'
                    else:
                        data = cursor.fetchall()

                    # convert to strings, not all types convert to JSON
                    data = [ [ str(item) for item in row ] for row in data ]

                    columns = [ el[0] for el in cursor.description ]

                    results.append({ 'query' : query,
                                     'comment' : comment,
                                     'data' : data ,
                                     'columns' : columns,
                                     'limit_message' : limit_message
                                     })
                except pg.Error as e:
                    results.append({ 'query' : query, 'comment' : comment, 'error' : str(e) })
                    break
            else:
                query = query + ';'
                try:
                    cursor.execute(query)
                    rowcount = cursor.rowcount
                    results.append({ 'query' : query, 'comment' : comment, 'message' : cursor.statusmessage })
                except pg.Error as e:
                    results.append({ 'query' : query, 'comment' : comment, 'error' : str(e) })
                    break

        cursor.close()
        connection.close()
        return json.dumps(results)

    except (Exception, pg.Error) as error :
        app.logger.exception(error)
        # connection = None
        return jsonify({ 'message': 'Connection Failed' }), 401



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
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def login():

    username = request.json['username'].strip()
    password = request.json['password'].strip()

    if not username:
        return jsonify({"message": "Missing username parameter"}), 400
    if not password:
        return jsonify({"message": "Missing password parameter"}), 400

    if authorize_login(username, password):

        if username not in session:
            byte_pass = password.encode()
            f = Fernet(app.secret_key)
            encrypt_pass = f.encrypt(byte_pass)
            session['username'] = username
            session['password'] = encrypt_pass

            return jsonify({'username': username, 'authorized': True}), 200
        else:
            return jsonify({'username': username, 'authorized': True}), 200

    else:
        app.logger.error("Not authorize_login")
        return jsonify({'username': username, 'authorized': False}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return jsonify({'success': True})

@app.route("/api/is_logged_in")
def is_logged_in():
    if 'username' in session:
        return jsonify({ 'loggedIn': True })
    else:
        return jsonify({ 'loggedIn': False })


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")
