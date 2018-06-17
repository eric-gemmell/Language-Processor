import MySQLdb
import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords  
from nltk.tree import Tree
import Tkinter
import pickle
Settings = {}
with open('ParsedTextToDataTableSettings.pckl',"rb") as f:
    try:
	Settings = pickle.load(f)
    except Exception as e:
	print(str(e))

def ExtractTuples(structured_sentences):
    ListOfTuples = []
    for SubChunk in structured_sentences:
        if(type(SubChunk) != tuple):
            Extracted = ExtractTuples(SubChunk)
            if Extracted:
                for Word in Extracted:
                    ListOfTuples.append(Word)
        else:
            ListOfTuples.append(SubChunk)
    return ListOfTuples

def GetType(Type,structured_sentence,PenetrateClause):
    #Recursive function, structured_sentence cannot be a tuple aka ("Eric",NNS)
    #Returns an array of Type parse trees.
    Chunks = []
    for SubChunk in structured_sentence:
        if(type(SubChunk) != tuple):
            if(Type != "" and Type in SubChunk.label()):
                Chunks.append(SubChunk)
            elif("Clause" in SubChunk.label()):
		if(PenetrateClause):
                    Result = GetType(Type,SubChunk,PenetrateClause)
                    if Result:
                    	Chunks = Chunks + Result
	    elif Type == "":
		Chunks.append(SubChunk)
	    else:
                Result = GetType(Type,SubChunk,PenetrateClause)
                if Result:
                    Chunks = Chunks + Result
	    
    return Chunks            
def SummedText(ListOfTuples): # needs to be improved... Or if not improved, the search mecanism need not to relly on writting the text perfectly
    Text = ""
    for index in range(len(ListOfTuples)):
	Text += ListOfTuples[index][0]
	if(index < (len(ListOfTuples)-1)):
	    Text += " "
    return Text

def GenerateChunkStructure(Chunk):
    structured_array = []
    ListOfTuples = ExtractTuples(Chunk)
    if(len(ListOfTuples) > 1):
    	structured_array.append(SummedText(ExtractTuples(Chunk)))
    for Tuple in ListOfTuples:
	structured_array.append(Tuple[0])
    return structured_array

def GenerateStructure(structured_sentence):
    #Generates an array of arrays, this way each level will be associated with the other words on the same level.
    #[[Tree(Carlos, Gemmell...),[Tree(my, brother...)]][Tree(is...)]]
    #--> [Carlos Gemmell is my brother,[Carlos Gemmell,(Carlos,NNP), (Gemmell,NNP)],[(is,VBZ)],[my brother, (my,PRP$), (brother,NN)]]
    structured_array = []
    structured_array.append(SummedText(ExtractTuples(structured_sentence)))
    #print GetType("Clause",structured_sentence,False)
    #print [GetType("SNom",Chunk,False) for Chunk in structured_sentence]
    #print [GetType("",Chunk,False) for Chunk in structured_sentence]
    if(Settings["SavedChunkType"] == "all"):
    	for Chunk in GetType("",structured_sentence,False):
   	    structured_array.append(GenerateChunkStructure(Chunk))
   	for Chunk in GetType("Clause",structured_sentence,False):
	    structured_array.append(GenerateStructure(Chunk))
    else:
    	for Chunk in GetType("SNom",structured_sentence,False):
   	    structured_array.append(GenerateChunkStructure(Chunk))
   	for Chunk in GetType("SVerb",structured_sentence,False):
	    structured_array.append(GenerateChunkStructure(Chunk))
   	for Chunk in GetType("Clause",structured_sentence,False):
	    structured_array.append(GenerateStructure(Chunk))
    return structured_array

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

def SimplifyTree(structured_sentence):
    #This function removes single branched trees
    if(type(structured_sentence) != tuple):
	if(len(structured_sentence) == 1):
	    structured_sentence = structured_sentence[0]
	    try:
	    	structured_sentence.draw()
	    except:
		print "error"
	    structured_sentence = SimplifyTree(structured_sentence)
	else:
	    for index in range(len(structured_sentence)):
		structured_sentence[index] = SimplifyTree(structured_sentence[index])
    try:
    	structured_sentence.draw()
    except:
   	print"error"
    return structured_sentence		

def Process(structured_sentences,text):
    for structured_sentence in structured_sentences:
	print GenerateStructure(structured_sentence)
