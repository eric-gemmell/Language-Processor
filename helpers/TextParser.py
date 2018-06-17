import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.tree import Tree
import Tkinter
import pickle

def MakeIndividualSentences(Paragraph):
    '''
    Outputs a list of sentences from a paragraph

    Parameters:
    -----------
    Paragraph: string
	Initial Unprocessed string directly from userinput
	Can be One or Multiple Sentences	

    Return:
    --------
    sentences: List
	List of sentences to be processed

    Exceptions:
    -----------
  
    '''
    sentences = sent_tokenize(Paragraph)
    #DO SPLITTING HERE
    return sentences

def FindTimeMarkers(tagged):
    '''
    Changes Part of Speech tags to ComplementT (ComplementTime) for words such as "Today", "night"
    These words are chosen from the pickle file "timemarkers.pckl"
    In Order to change which words are time markers, use the python program AddTimeMarker.py

    Parameters:
    -----------
    tagged: List of Tuples
	A list of words in a sentence with their associated tags Eg:[("Carlos","NNP"),("Today",NN")]

    Return:
    --------
    tagged: List of Tuples
	A list of words in a sentence with their associated tags Eg:[("Carlos","NNP"),("Today",ComplementT")]

    Exceptions:
    -----------
  
    '''
    with open('helpers/timemarkers.pckl',"rb") as f:
        TimeMarkers = []
        try:
            TimeMarkers = pickle.load(f)
        except Exception as e:
            print(str(e))

    for a in range(0,len(tagged)):
        if(tagged[a][0].lower() in TimeMarkers):
            tagged[a] = (tagged[a][0],"ComplementT")

    return tagged
def UnChunk(structured_sentence, Type):#Finds a specific chunk type, unchunks it
    '''
    Takes in structured_sentence at a certain level of parsing,
    Outputs the same parse, but having undone the specified chunk type

    Parameters:
    -----------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Type: string
	The type of Chunk to be removed, for example "SNom" 

    Return:
    --------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Exceptions:
    -----------
  
    '''
    for ChunkIndex in range(len(structured_sentence)):
        if(type(structured_sentence[ChunkIndex]) !=  tuple):
            if(structured_sentence[ChunkIndex].label() == Type):
                for SubChunk in structured_sentence[ChunkIndex]:
                    structured_sentence.insert(ChunkIndex, SubChunk)
                    ChunkIndex += 1
                del structured_sentence[ChunkIndex]

    return structured_sentence

def SplitSuccessive(structured_sentence, ChunkType, SubChunkType):
    '''
    Two Chunks of the same type can get parsed together into one large one
    For example two successive SNom Chunks get grouped into one large SNomDeactivated Chunk
    This function splits the second one out of the large chunk, as chinking will not work

    Parameters:
    -----------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    ChunkType: string
        The specific chunk type inside which you would like to split the two successive chunks, "SNomDeactivated" for example

    SubChunkType: string
        The specific SubChunk type which you would like to split the two successive chunks if there are any, "SNom" for example
	
    Return:
    --------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Exceptions:
    -----------
  
    '''
    for ChunkIndex in range(len(structured_sentence)):
        if(type(structured_sentence[ChunkIndex]) !=  tuple):
            if(structured_sentence[ChunkIndex].label() == ChunkType):
                PreviousChunkType = ""
                for SubChunk in structured_sentence[ChunkIndex]:
                    if(type(SubChunk) != tuple and type(SubChunk) != list):
                        if(SubChunk.label() == PreviousChunkType == SubChunkType):
                            structured_sentence.insert(ChunkIndex+1,SubChunk)
                            structured_sentence[ChunkIndex].remove(SubChunk)
                        PreviousChunkType = SubChunk.label()
                    else:
                        print SubChunk[1] 
                        if(SubChunk[1] == PreviousChunkType == SubChunkType):
                            structured_sentence.insert(ChunkIndex+1,SubChunk)
                            structured_sentence[ChunkIndex].remove(SubChunk)
                        PreviousChunkType = SubChunk[1]

    return structured_sentence

def RemoveNIChunks(structured_sentence):
    '''
    Removes branches that don't add extra information to the final parse, these being tagged by .*NI.*  
    Takes in the ParsedSentence after UncertainGrammar has been applied
    Uses the rules defined and applied in UncertainGrammar

    Parameters:
    -----------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Return:
    --------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Exceptions:
    -----------
  
    '''
    if(type(structured_sentence) != tuple):
	for index in range(len(structured_sentence)):
	    structured_sentence[index] = RemoveNIChunks(structured_sentence[index])

	if("NI" in structured_sentence.label()):#"NI" means NO INFORMATION, therefore that the additional chunk does nothing
	    label = structured_sentence.label().replace("NI","")
	    Inside = Tree(label,[])	   
		
	    for Chunk in structured_sentence:
	 	if "Clause" in Chunk.label():
		    for SubChunk in Chunk:
			Inside.append(SubChunk)
		else:
		    Inside.append(Chunk)
	    structured_sentence = Inside
    return structured_sentence
def ApplyVerbGrammar(tagged):
    '''
    Generates a nltk parse tree, structured_sentence, from the list of tagged entries, only having applied basic grammatical rules to Verbs,
    Adjectives, Injunctions and Adverbs

    Parameters:
    -----------
    tagged: List of Tuples
	A list of words in a sentence with their associated tags Eg:[("Carlos","NNP"),("Today",ComplementT")]
    
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser
	Here structured_sentence is not the one used, but it can be inputed

    Return:
    --------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Exceptions:
    -----------
  
    '''

    VerbGrammar = r"""
    SAdv: {<RB.*>}
    SAdv: {<SAdv>{2,}}
    SAdv: {(<SAdv><,|CC>?)+<SAdv>}

    SAdj: {<CD>}
    SAdj: {<JJ.*>}
    SAdj: {<SAdj>{2,}}

    VBG: {<RP>+<VBG>}
    VBG: {<VBG><RP>+}
    VBG: {<SAdv>+<VBG>}

    VBS: {<RP>+<VB.*>}
    VBS: {<VB.*><RP>+}
    VBS: {<SAdv>+<VB.*>}
    VBS: {<MD><VB.*>}

    SVerb: {<SAdv>?<TO><VB.*>}
    SVerb: {<VB.*|SVerb><SAdv>?<TO>}
    SVerb: {<VB.*|SVerb>{2,}}
    SVerb: {<VBS|VBD|VB|VBN|VBP|VBZ>}

    SVerb: {(<SVerb><,|CC>?)+<SVerb>}

    IN: {<TO>}
    IN: {<DT|SAdj|ASAdv>+<IN>}
    IN: {<IN><WP>}
    IN: {<IN>{2,}}

    SubVerb: {<IN><SVerb|VBG><IN>?}
                    
    """
    cp = nltk.RegexpParser(VerbGrammar,loop = 3)
    structured_sentence = cp.parse(tagged)
    return structured_sentence

def ApplyNounGrammar(structured_sentence):
    '''
    Applies Noun Grammar rules to the already Verb Grammar applied structured_sentence, returns same type
    These generaly are correct, errors are more often due to incorrect tagging

    Parameters:
    -----------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Return:
    --------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Exceptions:
    -----------
  
    '''

    NounGrammar = r"""
    SAdj: {<CD>}
    SAdj: {<VBG>}
    SAdj: {<JJ.*>}
    SAdj: {<SAdj>{2,}}
    SAdv: {<RB.*>}
    SAdv: {<SAdv>{2,}}
    SAdj: {<SAdv><SAdj>}
    SAdj: {<DT><SVerb>}
    SAdj: {(<SAdj><,|CC>?)+<SAdj>}
    SNom: {<NN|NNS>+}
    SNom: {<NNP|NNPS>+}
    SNom: {<SAdj>+<SNom>}
    SNom: {<PRP>}
    Det: {<DT|PRP.*>+}
    ComplementT: {<ComplementT>{2,}}
    ComplementT: {<Det|IN|SAdj>+<ComplementT>+} 
    ComplementTDeactivated: {<.*Verb><.*>*<ComplementT><.*>*<.*Verb>}
  	                    }<S.*|De.*|,|IN|V.*|CC|EX>{
    ComplementTActivated: {<ComplementT>}
    ComplementT: {(<ComplementTActivated><,|CC>?)+<ComplementTActivated>}
    """
    cp = nltk.RegexpParser(NounGrammar)
    structured_sentence = cp.parse(structured_sentence)
    structured_sentence = UnChunk(structured_sentence, "ComplementTDeactivated")
    structured_sentence = UnChunk(structured_sentence, "ComplementTActivated")

    NounGrammar = r"""
    SNom: {<Det><SNom|SAdj>}
    SNom: {<SNom><POS><SNom>}
    SNom: {<SAdj><.*Verb|IN>}
          }<SVerb|IN>{
                
    Complement: {<SAdj>}
    SNomDeactivated: {<.*Verb><.*>*<SNom><.*>*<.*Verb>}
                     }<Complement.*|SA.*|,|De.*|IN|.*V.*|V.*|CC|EX>{
    SNomActivated: {<SNom>}
    SNom: {(<SNomActivated><,>)*<SNomActivated><CC><SNomActivated>}
    """
    cp = nltk.RegexpParser(NounGrammar)
    structured_sentence = cp.parse(structured_sentence)
    structured_sentence = UnChunk(structured_sentence, "SNomDeactivated") 
    structured_sentence = UnChunk(structured_sentence, "SNomActivated") 

    NounGrammar = r"""
    SNomMerger: {<.*Verb|IN>(<SNom><,>)*<SNom><CC><SNom><IN|Complement.*|,|SNom>} 
                }<.*Verb|IN>{
    """
    cp = nltk.RegexpParser(NounGrammar)
    structured_sentence = cp.parse(structured_sentence)
    structured_sentence = SplitSuccessive(structured_sentence, "SNomMerger", "SNom")

    NounGrammar = r"""
    SNom: {<SNomMerger>}
    SNom: {<SNom><,>}
    ComplementActor: {<IN><SNom|Complement>}
    Complement:{<SAdv|RP>}
    Complement:{<SaNom>}
    """
    cp = nltk.RegexpParser(NounGrammar)
    structured_sentence = cp.parse(structured_sentence)

    return structured_sentence
def ApplyUncertainGrammar(structured_sentence):
    '''
    Applies Uncertain Grammar rules to the already VerbGrammar and NounGrammar applied structured_sentence, returns same type
    Improvement can be made here

    Parameters:
    -----------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Return:
    --------
    structured_sentence: Tree
        A sentence that has been parsed using nltk grammarparser

    Exceptions:
    -----------
  
    '''
    UncertainGrammar = r"""

    SubClause:{<IN><SNom>?<SVerb><Complement.*>*<SNom><Complement.*>*}
    SubClause:{<SubVerb><Complement.*>*<SNom|Complement.*><Complement.*>*}
    Clause:{<SNom|WDT|WP><SVerb><SNom>}
    SubClauseWithoutDC:{((<SNom>?<Complement.*>)|(<Complement.*><SNom>?))<SVerb>}
    ClauseWithoutDC:{<SNom|WDT><SVerb>}
    ClauseWithoutActor:{<SVerb><SNom|Complement.*>}
    Complement:{<SAdv>}

    SubClaNIuse:{<Complement.*><Cla.*useWithoutActor>}
    ClaNIuse:{<Cla.*use><Complement.*>+}
    ClaNIuse:{<Complement.*>+<,>?<Cla.*use>}
    ClaNIuseWithoutDC:{<Cla.*useWithoutDC><Complement.*>+}
    ClaNIuseWithoutActor:{<Cla.*useWithoutActor><Complement.*>+}

    SubClaNIuse:{<IN><Cla.*use.*>}
    Clause:{<Clause><ClauseWithoutActor>}
    SubCla.*use:{<Complement.*><Cla.*useWithoutActor>}
    Nucleus:{<Complement><SubCla.*use>}
            }<SubCla.*use>{
    Complement:{<Nucleus><SubCla.*use>}
                   
    ClauseWithoutDC:{<Cla.*useWithoutDC><SubCla.*use>+}
    Clause:{<Cla.*useWithoutDC><Cla.*use.*>}
    SubClause:{<SubCla.*useWithoutDC><Cla.*use.*|SNom>}
    SubClaNIuseWithoutDC:{<SubCla.*useWithoutDC><Complement.*>+}

    Clause:{<Cla.*use|SNom><SVerb><SubCla.*use.*|Complement.*>*<Cla.*use.*><SubCla.*use.*|Complement.*>*}
    ClauseWithoutDC:{<Cla.*use|SNom><SVerb><SubCla.*use.*|Complement.*>*}
    ClauseWithoutActor:{<SVerb><SubCla.*use.*|Complement.*>*<Cla.*use.*><SubCla.*use.*|Complement.*>*}
    Clause:{<Cla.*use><SubCla.*use.*>+}
    ClaNIuse:{<Cla.*use><Complement.*>+}
    ClauseWithoutDC:{<Cla.*useWithoutDC><Complement.*>+}
    ClaNIuseWithoutDC:{<Cla.*useWithoutDC><Complement.*>+}
    ClauseWithoutActor:{<Cla.*useWithoutActor><SubClaNIuse.*>+}
    ClaNIuseWithoutActor:{<Cla.*useWithoutActor><Complement.*>+}
    """

    cp = nltk.RegexpParser(UncertainGrammar,loop = 2)
    structured_sentence = cp.parse(structured_sentence)
    return structured_sentence

def Process(string):

	try:
                sentences = MakeIndividualSentences(string)
                structured_sentences = []
                for sentence in sentences:
                    words = nltk.word_tokenize(sentence)
		    tagged = nltk.pos_tag(words)

                    tagged = FindTimeMarkers(tagged)
                    print tagged
                    structured_sentence = ApplyVerbGrammar(tagged)
		    structured_sentence = ApplyNounGrammar(structured_sentence)
		    structured_sentence = ApplyUncertainGrammar(structured_sentence)
		    structured_sentence = RemoveNIChunks(structured_sentence)

                    structured_sentence.draw()
                    structured_sentences.append(structured_sentence)
                    #StructureParser(structured_sentence)
                return structured_sentences
       	except Exception as e:
		print(str(e))
