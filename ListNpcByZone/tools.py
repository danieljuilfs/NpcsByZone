from sqlalchemy import create_engine

def dbconnect(database):

    #create sql engine
    user = 'username'
    password = 'password'
    host = 'localhost'
    
    #string for connecting
    conn_string = f"mysql+pyodbc://{user}:{password}@{host}/{database}?driver=MySQL ODBC 8.4 ANSI Driver"

    #create the engine
    engine = create_engine(conn_string); 

    #return the engine
    return engine
    
    