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
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta
from psycopg2 import Error
from cryptography.fernet import Fernet

app = Flask(__name__,
            static_folder = "../dist/static",
            template_folder = "../dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['JWT_SECRET_KEY'] = 'Super_Secret_JWT_KEY'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

print(app.config)

CORS(app)
jwt = JWTManager(app)

# from app import routes
