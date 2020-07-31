from flask import Flask, render_template, jsonify, session
from random import *
from flask_cors import CORS
import requests
from flask import request
import psycopg2 as pg 
import pandas as pd 
import pandas.io.sql as psql 
from tabulate import tabulate
from psycopg2 import Error
import json

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/api/query', methods=['POST'])
def execute_query():
    try:
        connection = pg.connect(user = "jdbrant",
                                    password = "jimmy123",
                                    host = "flowers.mines.edu",
                                    port = "5433",
                                    database = "coursedev")
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
        except:
            print("Cannot fetch Query:", query)
            return None

    except (Exception, pg.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
        app.logger.exception(error)
        return None
    finally:
        #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                # print("PostgreSQL connection is closed")

# These are leftovers from previous build
@app.route('/api/random')
def random_number():
    response = {
        'randomNumber': randint(1, 100)
    }
    return jsonify(response)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")
