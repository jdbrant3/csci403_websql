from flask import Flask, render_template, jsonify
from random import *
from flask_cors import CORS
import requests
import psycopg2 as pg 
import pandas as pd 
import pandas.io.sql as psql 
from tabulate import tabulate
from psycopg2 import Error

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/api/query')
def execute_query():
    try:
        connection = pg.connect(user = "jdbrant",
                                    password = "jimmy123",
                                    host = "flowers.mines.edu",
                                    port = "5433",
                                    database = "coursedev")

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        # print ( connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        # cursor.execute("SELECT version();")
        # record = cursor.fetchone()
        # print("You are connected to - ", record,"\n")
    

        try:
            # query = "SELECT concat(first,' ', last) as name, school, known_for as description FROM pioneers.pioneers_people WHERE school = 'Stanford University';"
            # print("Enter SQL query:", end=' ')
            # query = input()
            query = "SELECT last, first FROM pioneers.pioneers_people;"
            table = pd.read_sql(query, connection)
            # df = pd.DataFrame(table)
            # print(tabulate(df, headers = df.columns, tablefmt = 'psql'))
            return table.to_json(orient='records')
        except:
            print("Cannot fetch Query:", query)

    except (Exception, pg.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                # print("PostgreSQL connection is closed")

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
