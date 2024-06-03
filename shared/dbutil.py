from sqlalchemy import create_engine

def dbconnect(database):

    #create sql engine
    user = 'itp246'
    password = 'itp246'
    host = 'localhost'
    
    #string for connecting
    conn_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"

    #create the engine
    engine = create_engine(conn_string); 

    #return the engine
    return engine
    
    