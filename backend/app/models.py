# from peewee import CharField, Model, MySQLDatabase
# from app import app
# import psycopg2 as pg
# import json

# with open('db_conn_config.json') as config_file:
#             conn_config = json.load(config_file)

# db = pg.connect(user = 'root', password = 'root', host = conn_config['host'], port = conn_config['port'], database = conn_config['dbname'])



# class BaseModel(Model):
#     class Meta:
#         database = db


# class Users(BaseModel):
#     username = CharField()
#     password = CharField()