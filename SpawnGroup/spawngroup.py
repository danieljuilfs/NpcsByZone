#code by juff, webdesign by rari, css by juff and rari
from flask import Flask, render_template, request, jsonify
from sqlalchemy import text
from ..shared import dbutil

app = Flask(__name__)

#query for getting npc data
getnpc = 'SELECT npc_types_patch.id, npc_types_patch.name, npc_types_patch.loottable_id, spawnentry.chance FROM npc_types_patch JOIN spawnentry ON spawnentry.npcID = npc_types_patch.id WHERE spawnentry.spawngroupID = :id'

#get the engine
engine = dbutil.dbconnect('eq25'); 

#serve up the starting page
@app.route("/spawngroups")
def index():
    return render_template('spawngroups.html')

#create a new spawn group
@app.route("/creategroup", methods=['POST'])
def create_spawngroup(): 

    #get both values out of the form. 
    name = request.form['spawnname'] 
    id = request.form['spawnid']

    print(id)
    #if the name exists, make it a string for passing to mysql. 
    if name:
        group = [id, name]

    #if both the name and the id exist
    if name and id:
        #query check to see if the id exists
        test = 'SELECT * FROM spawngroup WHERE id = :id OR name = :name'

        #query for creation
        insert = 'INSERT INTO spawngroup (id, name) VALUES (:id, :name)'

        with engine.connect() as connection:
            #run query to see if row already exists
            check = connection.execute(text(test), {'id' : id, 'name' : name})

            #query get the results set
            results = check.fetchone()

            #if the results set is empty, create the spawngroup
            if results is None:
                connection.execute(text(insert), { 'id' : id, 'name' : name})
                connection.commit()

                return render_template('editgroup.html', group=group)
        
            else: 
                #if it isn't empty, display an error. 
                return '<div class="err">Spawn Group ID or name already in use</div>', 400
    
    #if just the id exists, its a search for the id
    elif id: 

        #query check to see if the id exists
        test = 'SELECT * FROM spawngroup WHERE id = :id'

        with engine.connect() as connection:

            #execute the query
            check = connection.execute(text(test), {'id' : id})

            #get the results
            results = check.fetchone() 

            #if results is empty
            if results is None:
                return '<div class="err">The requested spawn group id does not exist</div>', 400
            
            #if the results do exist
            else:

                #prepare the query
                entries = connection.execute(text(getnpc), {'id' : id})

                #fetch the results 
                npcids = entries.fetchall()
                
                return render_template('editgroup.html', group=results, npcs=npcids, groupid=id)
            
    #if its just the name, its a search for things similar to the name
    elif name:
            
        #query to search
        search = "SELECT spawngroup.id, spawngroup.name, spawnentry.npcID, npc_types_patch.name FROM spawngroup JOIN spawnentry ON spawngroup.id=spawnentry.spawngroupID JOIN npc_types_patch on npc_types_patch.id = spawnentry.npcID WHERE spawngroup.name LIKE :name ORDER BY spawngroup.id ASC"

        with engine.connect() as connection:

            #prepare the query
            check = connection.execute(text(search), {'name' : f"%{name}%"})

            #execute the query
            npcgroups = check.fetchall()

            #list to append to
            appendlist = []

            for i in range (len(npcgroups)):
                group_id= npcgroups[i][0]
                group_name=npcgroups[i][1]

                if not any(group_id == group[0][0] for group in appendlist):

                    #list to store values in
                    grouplist = []
        
                    # Add group ID and group name to grouplist
                    grouplist.append([group_id])
                    grouplist.append([group_name])
                    
                    npcids = []
                    npcnames = []
                    #loop over the array again, check to see if the group id is in the list already, if it is, grab the npc id and put it in npc ids
                    for x in range (len(npcgroups)):
                    
                        #if the group id is in the list, add the npcs id to the npcid list
                        if npcgroups[x][0] == group_id:
                            npcids.append(npcgroups[x][2])
                            npcnames.append(npcgroups[x][3])

                    #append npcids to the list
                    grouplist.append(npcids)

                    #append npcnames to the list
                    grouplist.append(npcnames)

                    #append the full list to the appendlist
                    appendlist.append(grouplist)

            print(appendlist)

        return render_template('namesearch.html', appendlist=appendlist)        
                    
#update a spawngroups name
@app.route("/updatename", methods=['POST'])
def update_group_name():

    #get the name and id out of the form
    name = request.form['groupname'] 
    groupid = request.form['groupid']

    #query to check to see if the name is already in use
    namecheck = 'SELECT * FROM spawngroup WHERE name = :name'

    with engine.connect() as connection:
        #prepare the query
        check = connection.execute(text(namecheck), {'name' : name})

        #run the query
        results = check.fetchone()

        #if the query is empty, it means the name isnt in use so we can actually update with that value
        if results is None:
            insert = 'UPDATE spawngroup set name = :name where id = :id '

            #prepare the query
            connection.execute(text(insert), {'name' : name, 'id' : groupid})

            #commit the query
            connection.commit()

            return '<div class="success">Spawngroup name updated successfully</div>', 400

        #if it has results, return the failure
        else: 
            return '<div class="err">Name is already in use</div>', 400
        
#add npc to a spawngroup
@app.route("/addnpc", methods=['POST'])
def add_npc():

    #get the values out of the list
    npcid = request.form['npcid']
    chance = request.form['chance']
    groupid = request.form['groupid']

    #query to check if the mob is already in the group
    query = 'SELECT * FROM spawnentry WHERE spawngroupID = :groupid AND npcID = :npcid '

    with engine.connect() as connection: 
        #prepare the query
        check = connection.execute(text(query), {'groupid' : groupid, 'npcid' : npcid})

        #get the results
        results = check.fetchone()

        #check if results is empty, if it is, we can insert into the table because its unique
        if results is None:
            insert = 'INSERT into spawnentry (spawngroupID, npcID, chance) VALUES (:groupid, :npcid, :chance)'
            connection.execute(text(insert), {'groupid': groupid, 'npcid' : npcid, 'chance': chance })
            connection.commit()
            
            #prepare the query
            update = connection.execute(text(getnpc), {'id' : groupid})

            #execute the query getting the list of tuples
            updatelist = update.fetchall()

            #render the template returning the list
            return render_template('addnpc.html', updatelist=updatelist, groupid=groupid)
        else:
            return '<div class="err">Cannot have duplicate npcs in spawn group</div>', 400

#remove an npc from a spawngroup
@app.route("/removenpc", methods=['POST'])
def remove_npc():
    groupid = request.form['groupid']
    npcid = request.form['npcid']

    #query to remove the npc
    query = 'DELETE FROM spawnentry WHERE spawngroupID = :groupid AND npcID = :npcid'

    with engine.connect() as connection:
        #prepare the query
        connection.execute(text(query), {'groupid' : groupid, 'npcid': npcid})

        #commit the transaction
        connection.commit()

        #reload the page after deleting
        update = connection.execute(text(getnpc), {'id' : groupid})

        #execute the query getting the list of tuples
        updatelist = update.fetchall()

        #render the template returning the list
        return render_template('addnpc.html', updatelist=updatelist, groupid=groupid)

#update an npcs spawn chance
@app.route("/updatechance", methods=['POST'])
def update_chance():
    groupid = request.form['groupid']
    npcid = request.form['npcid']
    chance = request.form['chance']
    print(chance)

    query = 'UPDATE spawnentry SET chance = :chance WHERE spawngroupID = :groupid and npcID = :npcid'

    with engine.connect() as connection: 
        
        #prepare the query
        connection.execute(text(query), {'groupid' : groupid, 'npcid' : npcid, 'chance' : chance})

        #commit the query
        connection.commit()

        #get the data to update the page display. 
        #prepare the query
        update = connection.execute(text(getnpc), {'id' : groupid})

        #execute the query getting the list of tuples
        updatelist = update.fetchall()

        success = 'updated successfully'

        #render the template returning the list
        return render_template('updatenpc.html', updatelist=updatelist, groupid=groupid, success=success)

#clear the error tab
@app.route("/clear", methods=['POST'])
def clear_error():
        return ' '

#success mess
@app.route('/success', methods=['POST'])
def success():
    return '<div class="success">Spawn chance updated!</div>'
    
app.run()

