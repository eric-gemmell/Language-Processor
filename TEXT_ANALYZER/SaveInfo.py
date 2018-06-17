'''
NOT WORKING AT THE MOMENT, HAS NOT BEEN IMPLEMENTES
'''
import MySQLdb
import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords  
from nltk.tree import Tree
import Tkinter
import pickle

def CreateObject(Text,c,conn):
    #Checks for object in database, if there returns ID else inserts it in the database and returns ID
    c.execute("SELECT * FROM OBJECTS WHERE TEXT = '" + Text + "';")
    rowcount = c.rowcount
    if(rowcount == 0):
	c.execute("INSERT INTO OBJECTS (TEXT) VALUES ('"+Text+"');")
	conn.commit()
	return c.lastrowid
    else:
	return c.fetchall()[0][1]

def CreateLink(ID1,ID2,c,conn):
    c.execute("SELECT * FROM LINKS WHERE ID1 IN ("+str(ID1)+","+str(ID2)+") AND ID2 IN ("+str(ID1)+","+str(ID2)+");")
    rowcount = c.rowcount
    if rowcount == 0:
	c.execute("INSERT INTO LINKS (ID1,ID2,STRENGTH) VALUES ("+str(ID1)+","+str(ID2)+",3);")
	conn.commit()
    else:
	link = c.fetchall()[0]
	c.execute("UPDATE LINKS SET STRENGTH = ("+str(link[2]+3)+") WHERE ID1 = ("+str(link[0])+") AND ID2 = ("+str(link[1])+");")
	conn.commit()

def CreateInterObjectLinks(ObjectIDs,c,conn):
    for a in range(len(ObjectIDs)-1):
	for b in range(a+1,len(ObjectIDs)):
	    if(ObjectIDs[a] != ObjectIDs[b]):
	    	CreateLink(ObjectIDs[a],ObjectIDs[b],c,conn)

def CreateObjectTextLinks(ObjectIDs,TextID,c,conn):
    for a in range(len(ObjectIDs)-1):
	for b in range(a+1,len(ObjectIDs)):
	    if(ObjectIDs[a]!=ObjectIDs[b]):
		c.execute("INSERT INTO TEXT_LINKS (ID1,ID2,TEXT_ID) VALUES ("+str(ObjectIDs[a])+","+str(ObjectIDs[b])+","+str(TextID)+");") 
		conn.commit()

def RecursiveSave(StructuredArray,TextID,c,conn):
    ObjectIDs = []
    for Object in StructuredArray:
	if type(Object) != str:
	    ObjectIDs.append(CreateObject(Object[0],c,conn))
	else:
	    ObjectIDs.append(CreateObject(Object,c,conn))

    CreateInterObjectLinks(ObjectIDs,c,conn)
    CreateObjectTextLinks(ObjectIDs,TextID,c,conn)

    for a in range(len(StructuredArray)):
	if type(StructuredArray[a]) != tuple and type(StructuredArray[a]) != str:
	    RecursiveSave(StructuredArray[a],TextID,c,conn)

def SaveArray(StructuredArray,text):
    conn = MySQLdb.connect("127.0.0.1","BRAIN","brain","BRAIN")
    c = conn.cursor()
    c.execute("INSERT INTO TEXTS (TEXT) VALUES ('" +text+"');")
    conn.commit()
    TextID = c.lastrowid
    RecursiveSave(StructuredArray,TextID,c,conn)

