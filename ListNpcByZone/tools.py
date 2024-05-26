from sqlalchemy import create_engine

def dbconnect(database):

    #create sql engine
    user = ''
    password = ''
    host = 'localhost'
    

    try:
        #string for connecting
        conn_string = f"mysql+pyodbc://{user}:{password}@{host}/{database}?driver=MySQL ODBC 8.4 ANSI Driver"

        #create the engine
        engine = create_engine(conn_string); 

        #connect to the db
        connection = engine.connect()

        #return the connection
        return connection
    
    except Exception as e:
        print(e)
        raise