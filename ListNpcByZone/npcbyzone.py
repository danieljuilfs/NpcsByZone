#code by juff, webdesign by rari, css by juff and rari
from flask import Flask, render_template, request
from sqlalchemy import text
from ..shared import dbutil


app = Flask(__name__)

#get the engine
engine = dbutil.dbconnect('eq25'); 

@app.route("/npcbyzone")
def index():
    return render_template('zonenpcs.html')

@app.route("/loadnpcs", methods=['POST'])
def get_zones(): 

    #get the name out of the form
    shortname = request.form['shortname']

    #list to hold spawngroup ids
    zonemobs = []

    #quert get all mobs from spawn2 that match the zone
    spawn2 = """SELECT spawngroupID from spawn2 WHERE zone = :shortname"""
   
    with engine.connect() as connection:
        #execute the query to get mobs from spawn 2
        mobs = connection.execute(text(spawn2), { 'shortname' : shortname })
    
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

                #turn the id into a dictionary
                mob = {'id': row[0]}

                #query to get all the mobs from spawn group
                spawngroup = text("SELECT npc_types_patch.id FROM npc_types_patch JOIN spawnentry ON spawnentry.npcID = npc_types_patch.id  WHERE spawnentry.spawngroupid = :id;")
            
                #get execute the query based on the id
                sgids = connection.execute(spawngroup, mob)
            
                #get all the data
                data = sgids.fetchall()
            
                #for each row in the result, if its not already in the list add it
                for row in data:
                    if row[0] not in zonemobs:
                        zonemobs.append(row[0])
                          
        fullmobs = []
        #for each mob in zonemobs, get their name, mob id, loot table id
        for id in zonemobs:

            mob = {'id' : id}
            fullmob = text(f"SELECT npc_types_patch.id, npc_types_patch.name, npc_types_patch.loottable_id FROM npc_types_patch WHERE npc_types_patch.id = :id")
        
            #execute the query
            mobvalues = connection.execute(fullmob, mob)
        
            #get the mob data
            mobdata = mobvalues.fetchall()
        
            #shove the data in a table to pass
            for data in mobdata:
                fullmobs.append(data)

        #return the rendered page that displays the data. 
        return render_template('displaymobs.html', fullmobs=fullmobs)
    
app.run()

    



    
