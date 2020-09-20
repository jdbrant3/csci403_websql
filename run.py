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
from do_config import config

from pgspecial.main import PGSpecial
from pgspecial.namedqueries import NamedQueries

app = Flask(__name__,
            static_folder = "../dist/static",
            template_folder = "../dist")

# Define origins of api requests to enable Cross Origin Request Sharing for session object across api requests
cors = CORS(app, resources={r"/api/*": {'origins': ['http://localhost:8080', 'http://127.0,0,1:8000']}}, headers=['Content-Type'], expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True)

# Load app and database settings from config file
config(app)

pgspecial = PGSpecial()


def parse(query_string):
    # comments can occur both outside and inside queries; and semicolons can occur
    # inside comments.  This makes parsing tricky, if we want to retain comments
    # (relatively easy to just strip out all comments).
    multiline_comment = re.compile(r'(/\*.*?\*/)', flags = re.MULTILINE|re.DOTALL)
    single_line_comment = re.compile(r'(--.*$)', flags= re.MULTILINE)
    result = []

    current_comment = ''

    while True:
        query_string = query_string.strip()
        if len(query_string) == 0:
            break

        # what comes first?
        match = multiline_comment.match(query_string)
        if match:
            current_comment = current_comment + match.group(0) + '\n'
            query_string = query_string[(match.end()+1):]
            continue

        match = single_line_comment.match(query_string)
        if match:
            current_comment = current_comment + match.group(0) + '\n'
            query_string = query_string[(match.end()+1):]
            continue

        # else assume must be a query; however, we can't simply
        # search for a semicolon, because there could be a comment
        # embedded with a semicolon in it.  Find the first semicolon
        # not inside a comment.
        current_pos = 0
        while True:
            semi = query_string.find(';', current_pos)
            if semi == -1:
                semi = len(query_string)
            match = multiline_comment.search(query_string, current_pos)
            match2 = single_line_comment.search(query_string, current_pos)

            if match:
                if match2 and match2.start() < match.start():
                    match = match2
            else:
                match = match2

            if match and match.start() < semi and match.end() > semi:
                # comment enclosing, must look further
                current_pos = match.end() + 1
                continue

            # else, current semicolon is the end of this query
            current_query = query_string[0:semi]
            result.append((current_query, current_comment.strip()))
            query_string = query_string[(semi+1):]
            current_comment = ''
            break

    return result


@app.route('/api/query', methods=['POST'])
def execute_query():
    try:

        if 'username' not in session:
            return jsonify({'message': 'Not logged in'})

        else:
            session_username = session['username']
            f = Fernet(app.secret_key)
            session_password = f.decrypt(session['password']).decode('utf-8')

            connection = fetch_connection(session_username, session_password)
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
        return jsonify({ 'message': 'Connection Failed' }), 401


@app.route('/api/describe', methods=['GET'])
def describe():
    try:

        if 'username' not in session:
            return jsonify({'message': 'Not logged in'}), 400

        else:
            session_username = session['username']
            f = Fernet(app.secret_key)
            session_password = f.decrypt(session['password']).decode('utf-8')

            connection = fetch_connection(session_username, session_password)
            cursor = connection.cursor()

        for result in pgspecial.execute(cursor, "\d"):
            header = result[2]
        data = cursor.fetchall()
        data.insert(0, header)
        return json.dumps(data)
        
    except (Exception, pg.Error) as error :
        app.logger.exception(error)
        return jsonify({ 'message': 'Connection Failed' }), 401


@app.route('/api/describe_object', methods=['POST', 'GET'])
def describe_object():
    try:

        session_username = session['username']
        f = Fernet(app.secret_key)
        session_password = f.decrypt(session['password']).decode('utf-8')

        connection = fetch_connection(session_username, session_password)
        cursor = connection.cursor()

        for result in pgspecial.execute(cursor, "\dt"):
            header = result[2]
        data = cursor.fetchall()
        data.insert(0, header)
        return json.dumps(data)
        
    except (Exception, pg.Error) as error :
        app.logger.exception(error)
        return jsonify({ 'message': 'Connection Failed' }), 401


@app.route('/api/login', methods=['POST'])
def login():

    username = request.json['username'].strip()
    password = request.json['password'].strip()

    if authorize_login(username, password):
        
        # if user is not logged in already then create new session for user
        if username not in session:
            byte_pass = password.encode()
            f = Fernet(app.secret_key)
            encrypt_pass = f.encrypt(byte_pass)
            session['username'] = username
            session['password'] = encrypt_pass

            return jsonify({'username': username, 'authorized': True}), 200
        else:
            return jsonify({'username': username, 'authorized': True}), 200
    # If user not authenticated then return a flase authorization
    else:
        return jsonify({'username': username, 'authorized': False}), 200

# Remove user credentials from session object
@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return jsonify({'success': True})


# If connecting to database is successful then credentials are authenticated
def authorize_login(username, password):

    connection = fetch_connection(username, password)
    if connection:
        connection = None
        return True
    else:
        return False


def fetch_connection(username, password):
    try:
        connection = pg.connect(user = username,
                                password = password,
                                host = app.config['host'],
                                port = app.config['port'],
                                database = app.config['dbname'])

        connection.autocommit = True
        return connection
    except (Exception, pg.error) as error:
        app.logger.error(error)
        return None


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
