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

                    VBG: {<RP>+<VBG>}
                    VBG: {<VBG><RP>+}
                    VBG: {<RB>+<VBG>}

                    VBS: {<RP>+<VB.*>}
                    VBS: {<VB.*><RP>+}
                    VBS: {<RB>+<VB.*>}
                    VBS: {<MD><VB.*>}

                    SVerb: {<TO><VB.*>}
                    SVerb: {<VB.*|SVerb><TO>}
                    SVerb: {<VB.*|SVerb>{2,}}
                    SVerb: {<VBS|VBD|VB|VBN|VBP|VBZ>}
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
                    SNom: {<NN.*>}
                    SNom: {<SNom>{2,}}
                    SNom: {<SAdj>+<SNom>+}
                    SNom: {<PRP>}
                    Det: {<DT|PRP.*>?}
                    SNom: {<SAdj>}
                    SNom: {<Det><SNom>}
                    """
	            cp = nltk.RegexpParser(NounGrammar)
		    structured_sentence = cp.parse(structured_sentence)

                    GroupGrammar = r"""
                    IN:{<for><example>}
                    IN:{<IN>{2,}}
                    SNom: {<SNom><,>}
                    SNom:{(<SNom>+<CC>?)+<SNom>}
                    Clause:{<SNom|WDT><SVerb><SNom>}
                    ClauseWithoutDC:{<SNom|WDT><SVerb>}
                    ClauseWithoutActor:{<SVerb><SNom>}
                    Complement:{<IN><SNom>}
                    Complement:{<SAdv>}

                    Clause:{<Clause><Complement>+}
                    ClauseWithoutDC:{<ClauseWithoutDC><Complement>+}
                    ClauseWithoutActor:{<ClauseWithoutActor><Complement>+}

                    SubClause:{<IN><Clause|ClauseWithoutDC>}
                    Clause:{<Clause><ClauseWithoutActor>}


                    """
                    cp = nltk.RegexpParser(GroupGrammar)
                    structured_sentence = cp.parse(structured_sentence)

                    print structured_sentence
                    structured_sentence.draw()
                    #StructureParser(structured_sentence)

       	except Exception as e:
		print(str(e))

