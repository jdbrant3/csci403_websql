import psycopg2 as pg 
import pandas as pd 
import pandas.io.sql as psql 
from tabulate import tabulate
from psycopg2 import Error
try:
    connection = pg.connect(user = "jdbrant",
                                  password = "jimmy123",
                                  host = "flowers.mines.edu",
                                  port = "5433",
                                  database = "coursedev")

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")

    

    try:
        # query = "SELECT concat(first,' ', last) as name, school, known_for as description FROM pioneers.pioneers_people WHERE school = 'Stanford University';"
        # print("Enter SQL query:", end=' ')
        # query = input()
        query = "SELECT last, first FROM pioneers.pioneers_people;"
        table = pd.read_sql(query, connection)
        df = pd.DataFrame(table)
        # print(tabulate(df, headers = df.columns, tablefmt = 'psql'))
        print(df.to_json(orient='values'))
    except:
        print("Cannot fetch Query:", query)

except (Exception, pg.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")