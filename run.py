from flask import Flask, render_template, jsonify, session, request
from random import *
from flask_cors import CORS
import requests
import psycopg2 as pg
import json
import jwt
from datetime import datetime, timedelta
import re

from psycopg2 import Error

from cryptography.fernet import Fernet
#from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, JWTManager
#from pydantic import BaseModel

# from app.models import Users

app = Flask(__name__,
            static_folder = "../dist/static",
            template_folder = "../dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# jwt = JWTManager(app)
# app.config["JWT_SECRET_KEY"] = "naturally Hans is wet, he is standing under a waterfall"
AUTHSECRET = "naturally Hans is wet, he is standing under a waterfall"

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
                comment = comment + match.group(0);
                q = q[match.end():]
                continue

            match = single_line_comment.match(q)
            if match:
                comment = comment + match.group(0);
                q = q[match.end():]
                continue

            # if we found no leading comments, assume the rest is query
            break

        result.append((q.strip(), comment.strip()))

    return result


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
        app.logger.error("Line 76", error)
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
