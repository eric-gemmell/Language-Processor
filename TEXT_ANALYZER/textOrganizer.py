import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords
from nltk.corpus import state_union
import gender_guesser.detector as gender # for this to work you will need to run "sudo pip install -U gender-guesser"

#nltk.download("stopwords")
#nltk.download("punkt")
#nltk.download("state_union")
#nltk.download('averaged_perceptron_tagger')

d = gender.Detector(case_sensitive=False)
def GetGender(name):
    gender = d.get_gender(name)
    if((gender == "male")|(gender == "mostly_male")|(gender == "andy")):
        return "male"
    elif((gender == "female")|(gender == "mostly_female")):
        return "female"
    else:
        return "neutral"

class PronounTable:
    First_Person_Singular = " " #havent got it typed correctly yet
    Second_Person_Singular = " " 
    Third_Person_Singular_Masculin = " " 
    Third_Person_Singular_Feminin = " "
    Third_Person_Singular_Neutral = " "
    First_Person_Plural = " "
    Third_Person_Plural = " "
    PronounList = [["i","me"],["you"],["he","him"],["she","her"],["it"],["we","us"],["they","them"]]
    
def GetNouns_N(Chunk,mentioned_people):
    genderCount = [0,0,0]
    for Word in Chunk:
        if "NN" in Word[1]:
            gender = GetGender(unicode(Word[0], "utf-8"))
            print "Getting gender of " + Word[0]
            print gender 
            if(gender == "male"): 
                genderCount[0] += 1  
            elif(gender == "female"):
                genderCount[1] += 1
            else:
                genderCount[2] += 1
            print genderCount
    if((genderCount[0] == 0) and (genderCount[1] == 0)):
        print( "the Chunk " + str(Chunk) + " is neutral")
        mentioned_people.Third_Person_Singular_Neutral = Chunk
    elif(genderCount[0] >= genderCount[1]):
        print("The Chunk " + str(Chunk) + " is male") 
        mentioned_people.Third_Person_Singular_Masculin = Chunk
    else:
        print("The Chunk " + str(Chunk) + " is female")
        mentioned_people.Third_Person_Singular_Feminin = Chunk
    print"Added to Pronoun List\n"


def GetNouns_NA(Chunk,mentioned_people):  
    print ("Received the Nounified Adjective \"" + str(Chunk) + "\"")                                                                                                                          
    mentioned_people.Third_Person_Plural = Chunk                                                                                                                                               
    print "Added to Pronoun List\n" 

def GetNouns_GON(Chunk,mentioned_people):
    for index in range(0,len(Chunk)):
        SubChunk = Chunk[index]
        if(type(SubChunk) != tuple):
            if(SubChunk.label() == "P"):
                Chunk[index] = ReplacePronouns(SubChunk,mentioned_people)
                

    print ("Received the Group of Nouns \"" + str(Chunk) + "\"")
    mentioned_people.Third_Person_Plural = Chunk
    print "Added to Pronoun List\n"
    return Chunk

def ReplacePronouns(Chunk,mentioned_people):
    print Chunk[0][0]
    if Chunk[0][0].lower() in mentioned_people.PronounList[0]:
        Chunk = mentioned_people.First_Person_Singular 
        print "got a First Person Pronoun"

    elif Chunk[0][0].lower() in mentioned_people.PronounList[1]:
        Chunk = mentioned_people.Second_Person_Singular
        print "got a second person pronoun"

    elif Chunk[0][0].lower() in mentioned_people.PronounList[2]:
        Chunk = mentioned_people.Third_Person_Singular_Masculin
        print "got a third person pronoun masculin" 

    elif Chunk[0][0].lower() in mentioned_people.PronounList[3]:
        Chunk = mentioned_people.Third_Person_Singular_Feminin
        print "Got an singular neutral pronoun"

    elif Chunk[0][0].lower() in mentioned_people.PronounList[4]:
        Chunk = mentioned_people.Third_Person_Singular_Neutral
        print "Got an singular neutral pronoun"

    elif Chunk[0][0].lower() in mentioned_people.PronounList[5]:
        Chunk = mentioned_people.First_Person_Plural
        print mentioned_people.First_Person_Plural
        print "Got a First person plural pronoun"

    elif Chunk[0][0].lower() in mentioned_people.PronounList[6]:
        Chunk = mentioned_people.Third_Person_Plural
        print "Got a Third person plural"
    return Chunk

def GetActorsAndReplacePronouns(structured_sentence,mentioned_people):
    for index in range(0, len(structured_sentence)):
        Chunk = structured_sentence[index]
        print Chunk
        if(type(Chunk) != tuple):

            if(Chunk.label() == "N"):  
                GetNouns_N(Chunk,mentioned_people)

            elif(Chunk.label() == "NA"):
                GetNouns_NA(Chunk,mentioned_people)

            elif(Chunk.label() == "GROUP_OF_NOUNS"):                                                                                                                                             
                structured_sentence[index] = GetNouns_GON(Chunk,mentioned_people)

            elif(Chunk.label() == "P"):
                print Chunk
                structured_sentence[index] = ReplacePronouns(Chunk,mentioned_people)
                print "Post Pronoun"

            elif(Chunk.label() == "WORDS_WITH_COMA"):
                if(Chunk[0].label() == "N"):
                    GetNouns_N(Chunk[0],mentioned_people)
                elif(Chunk[0].label() == "NA"):
                    GetNouns_NA(Chunk[0],mentioned_people)
    return structured_sentence

def FilteredList (ListToFilter):
	return [w for w in ListToFilter if not w in set(stopwords.words("english"))]

def returnImportantWords(string):

        
	try:
                mentioned_people = PronounTable
                tagged = nltk.pos_tag(nltk.word_tokenize(sent_tokenize("The Eric ")[0]))
                grammar = r"""
                    N: {<DT>?<JJ.*>*<NN.*>+}
                    """
                cp = nltk.RegexpParser(grammar)
                mentioned_people.First_Person_Singular = cp.parse(tagged)[0][1]


                sentences = sent_tokenize(string)
                ImportantWords = []
                for i in sentences:
                    words = nltk.word_tokenize(i)
		    tagged = nltk.pos_tag(words)
		    grammar = r"""
			    VERB_COMPLEX: {<VB.*><RP>+<NN.*>*}
                            VERB_NOUN_COMPLEX: {<VB.*><DT>*<NN.*>+}
			    ADJECTIVISED_NOUN: {<JJ.*>*<NN.*>+}
                            NOUNIFIED_ADJECTIF: {<DT><JJ.*>+}"""
                    grammar = r"""
                            N: {<DT>?<JJ.*>*<NN.*>+}
                            NA: {<DT><JJ.*>+}
                            P: {<PRP>}
                            WORDS_WITH_COMA: {<P|N|NA><,>}
                            GROUP_OF_NOUNS: {<WORDS_WITH_COMA>*<P|N|NA><CC><P|N|NA|WORDS_WITH_COMA>}
                            """
                            #N -- ADJECTIVISED_NOUN -- any number of adjectives followed by any number of nouns
                            #NA -- NOUNIFIED_ADJECTIVE -- an adjective turned into a noun, as it has a determinant in front
                            #P -- PRONOUN

		    cp = nltk.RegexpParser(grammar)
		    result = cp.parse(tagged)
                    print result
                    result = GetActorsAndReplacePronouns(result,mentioned_people)
                    ImportantWords.append(result)
                return ImportantWords
       	except Exception as e:
		print(str(e))
print("Input Text")
text = raw_input("")

print(returnImportantWords(text))
