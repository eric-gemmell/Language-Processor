import MySQLdb
import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords  
from nltk.tree import Tree
import Tkinter
import pickle

def ExtractWords(Chunk):
    Words = []
    for SubChunk in Chunk:
        if(type(SubChunk) != tuple):
            Extracted = ExtractWords(SubChunk)
            if Extracted:
                for Word in Extracted:
                    Words.append(Word)
        else:
            Words.append(SubChunk)
    return Words

def GetType(Type,Chunk):
    #Recursive function, Chunk cannot be a tuple aka ("Eric",NNS)
    #Returns an array of Type parse trees.
    Chunks = []
    for SubChunk in Chunk:
        if(type(SubChunk) != tuple):
            if(SubChunk.label() == Type):
                Chunks.append(SubChunk)
            else:
                Result = GetType(Type,SubChunk)
                if Result:
                    Chunks = Chunks + Result

    return Chunks            
def SummedText(Chunk):
    Text = ""
    for NameTypeTuple in Chunk:
	Text += NameTypeTuple[0] + " "
    return Text

def GenerateStructure(ArrayOfChunks):
    #Generates an array of arrays, this way each level will be associated with the other words on the same level.
    #[[Tree(Carlos, Gemmell...),[Tree(my, brother...)]][Tree(is...)]]
    #--> [[Carlos Gemmell,(Carlos,NNP), (Gemmell,NNP)],[(is,VBZ)],[my brother, (my,PRP$), (brother,NN)]]
    StructuredArray = []
    for Chunks in ArrayOfChunks:
	for Chunk in Chunks:
	    ExtractedWords = ExtractWords(Chunk)
	    if(len(ExtractedWords) > 1):
	    	StructuredArray.append(ExtractedWords)
	    else:
	        StructuredArray.append(ExtractedWords[0])
    for index in range(len(StructuredArray)):
	if(type(StructuredArray[index]) != tuple):
	    StructuredArray[index].insert(0,SummedText(StructuredArray[index]))

    return StructuredArray

def RemoveObsolete(StructuredArray):
    #this part needs to be improved considerably
    #Right now it's the strict minimum for the program to work
    index = 0
    while index in range(len(StructuredArray)):
	if type(StructuredArray[index]) == tuple:
	    if StructuredArray[index][0] in set(stopwords.words("english")):
		del StructuredArray[index]
		index = index -1
	elif(type(StructuredArray[index]) == list):
	    StructuredArray[index] = RemoveObsolete(StructuredArray[index])
	index += 1
	
    return StructuredArray 
		

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
	    CreateLink(ObjectIDs[a],ObjectIDs[b],c,conn)

def CreateObjectTextLinks(ObjectIDs,TextID,c,conn):
    for a in range(len(ObjectIDs)-1):
	for b in range(a+1,len(ObjectIDs)):
	    c.execute("SELECT * FROM TEXT_LINKS WHERE ID1 IN ("+str(ObjectIDs[a])+","+str(ObjectIDs[b])+") AND ID2 IN ("+str(ObjectIDs[a])+","+str(ObjectIDs[b])+");")
	    rowcount = c.rowcount
	    if(rowcount == 0):
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

def Process(structured_sentences,text):
    Words = []
    Links = []
    Sentences = []
    SNoms = GetType("SNom",structured_sentences)
    SVerbs = GetType("SVerb",structured_sentences)
    #Should do Actor recognition here and remove all pronouns as well
    StructuredArray = GenerateStructure([SNoms,SVerbs])
    RemoveObsolete(StructuredArray)
    print(StructuredArray)
    SaveArray(StructuredArray,text)

