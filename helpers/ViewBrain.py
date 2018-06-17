import MySQLdb
import os

def GetRequest():
    print("Enter Stimulus to Receive a Response")
    word = raw_input("")
    Response(word)

def GetObject(ID,c,conn):
    c.execute("SELECT * FROM OBJECTS WHERE ID = '"+str(ID)+"';")
    return c.fetchall()[0][0]

def GetID(Object,c,conn):
    c.execute("SELECT * FROM OBJECTS WHERE TEXT = '"+Object+"';")
    if c.rowcount == 0:
	return -1
    return c.fetchall()[0][1]

def GetLinkedIDs(ID,c,conn):
    #Returns an array of IDs linked to the inputed one, ordered by strength, and associated to their text
    #[ID,Strength,TextIDs]
    c.execute("SELECT * FROM LINKS WHERE ID1 = "+str(ID)+" OR ID2 = "+str(ID)+";")
    Links = []
    for link in c.fetchall():	
	Links.append([part for part in link if(type(part) != list and part !=  ID)])

    for index in range(len(Links)):
    	c.execute("SELECT * FROM  TEXT_LINKS WHERE ID1 IN ("+str(Links[index][0])+","+str(ID)+") AND ID2 IN ("+str(Links[index][0])+","+str(ID)+");")
	result = c.fetchall()
	Links[index].append([TextLink[2] for TextLink in result])
    Links = sorted(Links,key=lambda x: (x[1]))  
    return Links
	

def Response(Text):
    conn = MySQLdb.connect("127.0.0.1","BRAIN","brain","BRAIN")
    c = conn.cursor()
    ID = GetID(Text,c,conn)
    Links = GetLinkedIDs(ID,c,conn)
    Links = Links[:min(10,len(Links))]
    Links = [[GetObject(Links[a][0],c,conn)] + Links[a][1:] for a in range(len(Links))] 
    for Link in Links:
	print Link
	print "\n"
    GetRequest()       

GetRequest()
