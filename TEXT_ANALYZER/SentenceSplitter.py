import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.tree import Tree
import Tkinter
import pickle

def MakeIndividualSentences(string):
    sentences = sent_tokenize(string)
    #DO SPLITTING HERE
    return sentences
def FindTimeMarkers(tagged):
    with open('timemarkers.pckl',"rb") as f:
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

    for ChunkIndex in range(len(structured_sentence)):
        if(type(structured_sentence[ChunkIndex]) !=  tuple):
            if(structured_sentence[ChunkIndex].label() == Type):
                for SubChunk in structured_sentence[ChunkIndex]:
                    structured_sentence.insert(ChunkIndex, SubChunk)
                    ChunkIndex += 1
                del structured_sentence[ChunkIndex]

    return structured_sentence
def SplitSuccessive(structured_sentence, ChunkType, SubChunkType):

    for ChunkIndex in range(len(structured_sentence)):
        if(type(structured_sentence[ChunkIndex]) !=  tuple):
            if(structured_sentence[ChunkIndex].label() == ChunkType):
                PreviousChunkType = ""
                for SubChunk in structured_sentence[ChunkIndex]:
                    if(type(SubChunk) != tuple and type(SubChunk) != list):
                        print SubChunk.label()
                        if(SubChunk.label() == PreviousChunkType == SubChunkType):
                            print "Got two Chunks of same type"
                            structured_sentence.insert(ChunkIndex+1,SubChunk)
                            structured_sentence[ChunkIndex].remove(SubChunk)
                        PreviousChunkType = SubChunk.label()
                    else:
                        print SubChunk[1] 
                        if(SubChunk[1] == PreviousChunkType == SubChunkType):
                            print "Got two Chunks of same type!" 
                            structured_sentence.insert(ChunkIndex+1,SubChunk)
                            structured_sentence[ChunkIndex].remove(SubChunk)
                        PreviousChunkType = SubChunk[1]

    return structured_sentence

def Process(string):

	try:
                sentences = MakeIndividualSentences(string)
                structured_sentences = []
                for i in sentences:
                    words = nltk.word_tokenize(i)
		    tagged = nltk.pos_tag(words)

                    tagged = FindTimeMarkers(tagged)
                    print tagged
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
                    #structured_sentence = UnChunk(structured_sentence,"SNomMerger")

                    NounGrammar = r"""
                    SNom: {<SNomMerger>}
                    SNom: {<SNom><,>}
                    ComplementActor: {<IN><SNom|Complement>}
                    Complement:{<SAdv|RP>}
                    Complement:{<SaNom>}
                    """
	            cp = nltk.RegexpParser(NounGrammar)
		    structured_sentence = cp.parse(structured_sentence)

                    UncertainGrammar = r"""

                    SubClause:{<IN><SNom>?<SVerb><Complement.*>*<SNom><Complement.*>*}
                    SubClause:{<SubVerb><Complement.*>*<SNom|Complement.*><Complement.*>*}
                    Clause:{<SNom|WDT|WP><SVerb><SNom>}
                    SubClauseWithoutDC:{((<SNom>?<Complement.*>)|(<Complement.*><SNom>?))<SVerb>}
                    ClauseWithoutDC:{<SNom|WDT><SVerb>}
                    ClauseWithoutActor:{<SVerb><SNom|Complement.*>}
                    Complement:{<SAdv>}

                    SubClause:{<Complement.*><ClauseWithoutActor>}
                    Clause:{<Clause><Complement.*>+}
                    Clause:{<Complement.*>+<,>?<Clause>}
                    ClauseWithoutDC:{<ClauseWithoutDC><Complement.*>+}
                    ClauseWithoutActor:{<ClauseWithoutActor><Complement.*>+}

                    SubClause:{<IN><Clause.*>}
                    Clause:{<Clause><ClauseWithoutActor>}
                    SubClause:{<Complement.*><ClauseWithoutActor>}
                    Nucleus:{<Complement><SubClause>}
                            }<SubClause>{
                    Complement:{<Nucleus><SubClause>}
                    
                    ClauseWithoutDC:{<ClauseWithoutDC><SubClause>+}
                    Clause:{<ClauseWithoutDC><Clause.*>}
                    SubClause:{<SubClauseWithoutDC><Clause.*|SNom>}
                    SubClauseWithoutDC:{<SubClauseWithoutDC><Complement.*>+}



                    Clause:{<Clause|SNom><SVerb><SubClause.*|Complement.*>*<Clause.*><SubClause.*|Complement.*>*}
                    ClauseWithoutDC:{<Clause|SNom><SVerb><SubClause.*|Complement.*>*}
                    ClauseWithoutActor:{<SVerb><SubClause.*|Complement.*>*<Clause.*><SubClause.*|Complement.*>*}
                    Clause:{<Clause><SubClause.*|Complement.*>+}
                    ClauseWithoutDC:{<ClauseWithoutDC><SubClause.*|Complement.*>+}
                    ClauseWithoutActor:{<ClauseWithoutActor><SubClause.*|Complement.*>+}
                    """

                    cp = nltk.RegexpParser(UncertainGrammar,loop = 2)
                    #structured_sentence = cp.parse(structured_sentence)

                    #structured_sentence.draw()
                    structured_sentences.append(structured_sentence)
                    #StructureParser(structured_sentence)
                return structured_sentences
       	except Exception as e:
		print(str(e))
