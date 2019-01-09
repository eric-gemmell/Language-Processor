#import MySQLdb
import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords  
from nltk.tree import Tree
import Tkinter
import pickle
Settings = {}
with open('helpers/ParsedTextToDataTableSettings.pckl',"rb") as f:
    try:
	Settings = pickle.load(f)
    except Exception as e:
	print(str(e))

def ExtractTuples(structured_sentences):###
    '''
    Recursively makes a list of all tuples from a text tree
    Parameters:
    -----------
    structured_sentences: Tree
        Sentences that have been parsed using nltk grammarparser

    Return:
    --------
    ListOfTuples: List of Tuples
	A list of all tuples aranged in sequence from the structured_sentences

    Exceptions:
    -----------  
    '''
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

def GetType(Type,structured_sentence,PenetrateClause):###
    '''
    Extracts the Specified Chunks,of type Type, from within a parsed Tree, structured_sentence. 
    PenetrateClause when set to true allows it to work recursively within Clauses.
    When Type = "" it returns all sub elements that are not Clauses in structured_sentence

    Parameters
    -----------
    Type: string
	The specified Chunk Type that will be returned, for example "SNom", "Complement", "Clause", "SVerb" etc.

    structured_sentence: Tree
	A sentence that has been parsed using nltk grammarparser

    PenetrateClause: bool
	Whether or not to recursively enter Clauses

    Return:
    --------
    Chunks: List of Trees
	The specified type of Chunks outputed as a list.

    Exceptions:
    -----------  
    Make sure inputed structured_sentence is an array/list of structured_sentences, as with PenetrateClause set to false, it will output nothing. Unless you know what you're doing...    
    '''
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
def SummedText(ListOfTuples):###
    #needs to be improved... Or if not improved, the search mecanism need not to relly on writting the text perfectly
    '''
    Turns a list of tuples into a string, does no fancy merging.

    Parameters
    -----------
    ListOfTuples: List of Tuples
	a list of the tuples forming the sentence.

    Return:
    --------
    Text: string
	the summed text from the tuples

    Exceptions:
    -----------  
    '''

    Text = ""
    for index in range(len(ListOfTuples)):
	Text += ListOfTuples[index][0]
	if(index < (len(ListOfTuples)-1)):
	    Text += " "
    return Text

def GenerateChunkStructure(Chunk):###

    '''
    From a chunk outputs a array of format ["sentence","word1","word2","word3"] 

    Parameters
    -----------
    Chunk: Tree
	a Nltk parsed tree 

    Return:
    --------
    structured_array: array of strings
	an array of format ["sentence","word1","word2","word3"]

    Exceptions:
    -----------  
    '''

    structured_array = []
    ListOfTuples = ExtractTuples(Chunk)
    if(len(ListOfTuples) > 1):
    	structured_array.append(SummedText(ExtractTuples(Chunk)))
    for Tuple in ListOfTuples:
	structured_array.append(Tuple[0])
    return structured_array

def GenerateStructure(structured_sentence):###

    '''
    GenerateStructure is a coordinating function, from each sentence tree, forms a multi dimensional array of format:
    ["sentence",["group1","word1","word2"],["group2","word1","word2",["subgroup1","word1","word2"]],etc...]
    this array to then be saved in the database

    Parameters
    -----------
    structured_sentence: Tree
	A sentence that has been parsed using nltk grammarparser

    Return:
    --------
    structured_array: array of arrays
	multi dimensional array of format:
	["sentence",["group1","word1","word2"],["group2","word1","word2",["subgroup1","word1","word2"]],etc...]
	this array to then be saved in the database

	each level will be associated with the other words on the same level.
        [[Tree(Carlos, Gemmell...),[Tree(my, brother...)]][Tree(is...)]]
        --> [Carlos Gemmell is my brother,[Carlos Gemmell,(Carlos,NNP), (Gemmell,NNP)],[(is,VBZ)],[my brother, (my,PRP$), (brother,NN)]]
  
    Exceptions:
    -----------  
    '''
    structured_array = []
    structured_array.append(SummedText(ExtractTuples(structured_sentence)))
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


def Process(structured_sentences,text):
    for structured_sentence in structured_sentences:
	print GenerateStructure(structured_sentence)


###
###
###
###
#USELESS ATM FUNCTIONS


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
