import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.tree import Tree
import Tkinter

def GetType(Chunk):
    if (type(Chunk) == tuple):
        return(Chunk[1])
    else:
        return Chunk.label()

def GetPredicate(structured_sentence_chunk):
    Predicate = []

    return Predicate
def StructureParser(structured_sentence):
    LastChunk = ""
    for index in range(0,len(structured_sentence)):
        Chunk = structured_sentence[index]
        print Chunk
        print GetType(Chunk) 
        if(GetType(Chunk) == ("WDT" or "WP")):
            print "Received a subordinate introducer, Getting Predicate"
            Predicate = GetPredicate(structured_sentence[(index):])
            print Predicate
        if(GetType(Chunk) =="SNom"):
            print "Received a SNom"
            
        LastChunk = Chunk
    return structured_sentence

def Process(string):

	try:
                sentences = sent_tokenize(string)
                ImportantWords = []
                for i in sentences:
                    words = nltk.word_tokenize(i)
		    tagged = nltk.pos_tag(words)

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
                    IN: {<DT|SAdj|SAdv>+<IN>}
                    IN: {<IN>{2,}}

                    SubVerb: {<IN><SVerb|VBG><IN>?}
                    SVerb: {<SVerb><IN>}
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
                    SNom: {<NN.*>}
                    SNom: {<SNom>{2,}}
                    SNom: {<SAdj>+<SNom>+}
                    SNom: {<PRP>}
                    Det: {<DT|PRP.*>+}
                    SNom: {<Det><SNom|SAdj>}
                    SNom: {<SNom><POS><SNom>}
                    SNom: {<SAdj><SVerb|IN>}
                          }<SVerb|IN>{
                    Complement: {<SAdj>}
                    SNom: {<SNom><,>}
                    ComplementActor: {<IN><SNom|Complement>}
                    Complement:{<SAdv|RP>}
                    """
	            cp = nltk.RegexpParser(NounGrammar)
		    structured_sentence = cp.parse(structured_sentence)

                    UncertainGrammar = r"""
                    SVerb:{<SVerb><Complement>}
                    SubClause:{<IN><SNom>?<SVerb><SNom>}
                    SubClause:{<SubVerb><SNom>}
                    Clause:{<SNom|WDT|WP><SVerb><SNom>}
                    SubClauseWithoutDC:{((<SNom>?<Complement.*>)|(<Complement.*><SNom>?))<SVerb>}
                    ClauseWithoutDC:{<SNom|WDT><SVerb>}
                    ClauseWithoutActor:{<SVerb><SNom|Complement.*>}
                    Complement:{<SAdv>}

                    SubClause:{<Complement.*><ClauseWithoutActor>}
                    Clause:{<Clause><Complement.*>+}
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
                    structured_sentence = cp.parse(structured_sentence)

                    print structured_sentence
                    structured_sentence.draw()
                    #StructureParser(structured_sentence)

       	except Exception as e:
		print(str(e))
