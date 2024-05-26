#code by juff, webdesign by rari, css by juff and rari
from flask import Flask, render_template, request, session
from sqlalchemy import text
import tools
import os

app = Flask(__name__)

#get the engine
engine = tools.dbconnect('eq25'); 

@app.route("/")
def index():
    return render_template('zonenpcs.html')

@app.route("/loadnpcs", methods=['POST'])
def get_zones(): 
    shortname = request.form['shortname']

    #list to hold spawngroup ids
    zonemobs = []

    parameters = (shortname,)
    #get all mobs from spawn2 that match the zone
    spawn2 = (f"SELECT spawngroupID from spawn2 WHERE zone = '{shortname}'")
    #spawn2 = "SELECT spawngroupID from spawn2 WHERE zone = ?")
   
    with engine.connect() as connection:
        #execute the query to get mobs from spawn 2
        mobs = connection.execute(text(spawn2))
    
        #fetch all the mobs in spawn groups
        rows = mobs.fetchall() 
    
        #iterate over the returned data and add to array
        for row in rows:
       
            #get every solo mob above 3mil;
            if (row[0] > 3000000) and (row[0]-3000000 not in zonemobs):
                zonemobs.append(row[0]-3000000)
            
            #get every solo mob above 1mil
            elif (row[0]) > 1000000 and (row[0]-1000000 not in zonemobs):
            
                zonemobs.append(row[0] - 1000000)
            
            else:
                #query to get all the mobs from spawn group
                spawngroup = text(f"SELECT npc_types.id FROM npc_types JOIN spawnentry ON spawnentry.npcID = npc_types.id  WHERE spawnentry.spawngroupid = '{row[0]}';")
            
                #get execute the query based on the id
                sgids = connection.execute(spawngroup)
            
                #get all the data
                data = sgids.fetchall()
            
                #for each row in the result, if its not already in the list add it
                for row in data:
                    if row[0] not in zonemobs:
                        zonemobs.append(row[0])
                          
   

        fullmobs = []
        #for each mob in zonemobs, get their name, mob id, loot table id
        for id in zonemobs:
            fullmob = text(f"SELECT npc_types.id, npc_types.name, npc_types.loottable_id FROM npc_types WHERE npc_types.id = {id}")
        
            #execute the query
            mobvalues = connection.execute(fullmob)
        
            #get the mob data
            mobdata = mobvalues.fetchall()
        
            #shove the data in a table to pass
            for data in mobdata:
                fullmobs.append(data)

        #return the rendered page that displays the data. 
        return render_template('displaymobs.html', fullmobs=fullmobs)
    
app.run()

    



    
