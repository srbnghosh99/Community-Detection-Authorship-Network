from flask import Flask
from flask import jsonify
import networkx as nx
from datetime import datetime
import csv
from flask import Flask,render_template,request
import json

app = Flask(__name__)
G = nx.Graph()

nonoverlappingcommunity_vertexmap={}  #nonoverlappingcommunity_vertexmap[cdlgoname:str][vertexid:str]:int
nonoverlappingcommunity_communitymap={} #nonoverlappingcommunity_vertexmap[cdalgoname:str][communityid:int]:list:str
overlappingcommunity_vertexmap={}  #nonoverlappingcommunity_vertexmap[cdlgoname:str][vertexid:str]:int
overlappingcommunity_communitymap={} #nonoverlappingcommunity_vertexmap[cdalgoname:str][communityid:int]:list:str


def load_graph(edgelist_filename: str):
    global G
    print("Starting to load graph at =", datetime.now().strftime("%H:%M:%S"))
    G = nx.read_edgelist(edgelist_filename, delimiter=" ", data=(("weight", int),))
    print("Finished loading graph at =", datetime.now().strftime("%H:%M:%S"))
    print()

# returns a JSON where ["data"] is a list of  vertexid:str
@app.route('/vertices')
def vert():
    ret={}
    ret["data"] = list(G.nodes)
    ret["status"] = "OK"
    return jsonify(ret)

# returns a JSON where ["data"] is a list of neighbors:str of that vertex
@app.route('/neighborsof/<vertex_id>')
def neighbor(vertex_id: str):
    ret = {}
    ret["status"] = "OK"
    ret["data"] = list (G.neighbors(vertex_id))
    return jsonify(ret)

#returns a JSON where ["data"][vertexid] is a communityid:int
@app.route('/community/<community_name>/vertex/<vertex_id>')
def community_of(community_name:str, vertex_id: str):
    ret = {}
    data = {}

    try:
        data[vertex_id] = nonoverlappingcommunity_vertexmap[community_name][vertex_id]
        ret["status"] = "OK"
        ret["data"] = data
    except:
        ret["status"] = "KO"
    
    return jsonify(ret)

#returns a JSON where ["data"][community_id] is a list of vertexid:str belonging to that community
@app.route('/community/<community_name>/all/<int:community_id>')
def community_all(community_name:str, community_id:int):
    ret={}

    try:
        communityset = nonoverlappingcommunity_communitymap[community_name][community_id]
        ret["data"] = {}
        ret["data"][community_id] = list(communityset) #set() are not JSON serializable in python
        ret["status"] = "OK"
    except:
        ret["status"] = "KO"

    return jsonify(ret)

#returns a JSON where data is a list of strings of available communities
@app.route('/communities')
def communities():
    ret = {}
    try:
        comm_info = {}
        communities_instore1 = nonoverlappingcommunity_communitymap.keys()
        lis1 = list(communities_instore1)
        for i in lis1:
            comm_info[i] =  len(nonoverlappingcommunity_communitymap[i])
        communities_instore2 = overlappingcommunity_communitymap.keys()
        lis2 = list(communities_instore2)
        for i in lis2:
            comm_info[i] =  len(overlappingcommunity_communitymap[i])
        ret["data"] = comm_info
        ret["status"] = "OK"
    except:
        ret["status"] = "KO"
    return jsonify(ret)
        
@app.route('/')
def index():
    return 'Web App with Python Flask!'

@app.route('/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        return render_template('data.html',form_data = form_data)

def build_nonoverlappingcommunitymap_fromvertexmap(commname:str):
    print(str)
    reversemap = {}
    vertexmap = nonoverlappingcommunity_vertexmap[commname]
    for vertexid in vertexmap:
        commid = vertexmap[vertexid]
        if commid not in reversemap:
            reversemap[commid] = set()
        reversemap[commid].add(vertexid)
    nonoverlappingcommunity_communitymap[commname]=reversemap

def build_overlappingcommunitymap_fromvertexmap(commname:str):
    print(str)
    reversemap = {}
    vertexmap = overlappingcommunity_vertexmap[commname]
    for vertexid in vertexmap:
        commid = vertexmap[vertexid]
        for i in commid:
            if i not in reversemap:
                reversemap[i] = set()
            reversemap[i].add(vertexid)
    overlappingcommunity_communitymap[commname]=reversemap


# loads a community file. Assume that the format of the file is:
#
# with a one line header
# Vertex Community
# vertexid:str communityid:int
def load_community_nonoverlapping(commname:str, filename:str):
    comm = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=' ')
        for row in reader:
            comm[row['Vertex']] = int(row['Community'])
        nonoverlappingcommunity_vertexmap[commname] = comm
        build_nonoverlappingcommunitymap_fromvertexmap(commname)

def load_community_overlapping(commname:str, filename:str):
    comm = {}
    print(filename)
    with open(filename, 'r') as f:
        comm = json.load(f)
        overlappingcommunity_vertexmap[commname] = comm
        build_overlappingcommunitymap_fromvertexmap(commname)


#load_graph('data/dblp-coauthor.edgelist')
load_graph('sample_HCI_coauthornet.edgelist')
load_community_nonoverlapping('Louvain', 'louvain_HCI.csv')
load_community_overlapping('EgoSplitting', 'Egosplitting_HCI_memberships.json')

if __name__ == "__main__":
    # app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', port=8080)
