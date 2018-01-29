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

    People = [["FPS","Undefined"],["SPS","Undefined"],["TPSM","Undefined"],["TPSF","Undefined"],["TPSN","Undefined"],["FPP","Undefined"],["SPP","Undefined"],["TPP","Undefined"]]
    PronounList = [["i","me","myself"],["you","yourself"],["he","him","himself"],["she","her","herself"],["it"],["we","us","ourselves"],["you","yourselves"],["they","them","themselves"]]
    
#
#
#
def Replace(Chunk,mentioned_people):
    print "Replacing Pronoun"
    print Chunk
    for index in range(0,len(mentioned_people.PronounList)):
        if(Chunk[0][0].lower() in mentioned_people.PronounList[index]):
            print "Found Pronoun type"
            print mentioned_people.People[index][0]
            if(mentioned_people.People[index][1] != "Undefined"):
                Chunk = mentioned_people.People[index][1]

    print Chunk
    return Chunk

def ReplacePronouns(Chunk,mentioned_people):
    if(type(Chunk) != tuple):
        if(Chunk.label() == "P"):
            print "Got a Pronoun, Changing Pronoun"
            print Chunk
            Chunk = Replace(Chunk,mentioned_people)
        elif(Chunk.label() == "GROUP_OF_NOUNS"):
            print "Got a Group of Nouns, Going through individual elements"
            print Chunk
            for index in range(0,len(Chunk)):
                print "Checking SubChunk"
                print Chunk[index]
                Chunk[index] = ReplacePronouns(Chunk[index],mentioned_people)
        elif(Chunk.label() == "WORDS_WITH_COMA"):
            print "Got a Word with a coma, checking it"
            print Chunk
            Chunk[0] = ReplacePronouns(Chunk[0],mentioned_people)
    return Chunk

def SetPersonalPronoun(actor,mentioned_people): 
    for index in range(0,len(mentioned_people.People)):
        if(mentioned_people.People[index][0] == actor[0]):
            print "Found the Pronoun spot for inserting into mentioned people"
            mentioned_people.People[index][1] = actor[1]
            print "Person Added"
            print mentioned_people.People
    return mentioned_people

def GetActors_N(Chunk):#here Chunk has to be of type N, a Noun
    List = []
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
    if((genderCount[0] == 0) and (genderCount[1] == 0)):#if nothing in the noun says it has gender, then it doesnt
        print( "the Chunk " + str(Chunk) + " is neutral")
        List.insert(0,["TPSN",Chunk])
    elif(genderCount[0] >= genderCount[1]):
        print("The Chunk " + str(Chunk) + " is male")# if male are dominant in the noun , in the sense that most of the Nouns in the Chunk are male, then the Chunk is male
        List.insert(0,["TPSM",Chunk])
    else:
        print("The Chunk " + str(Chunk) + " is female")#in the same way if females are dominant, the Chunk is female.
        List.insert(0,["TPSF",Chunk])

    print"Noun " +str(Chunk) + "has been added to the list\n"  
    #This function only recognizes people as possibly 3d person singular...
    return List 
    #Please note that I still havent fixed the issue of some nouns such as mother and father having a gender
    #Neither have i sorted out the problem of this function being able to recognize plural groups, 
    #maybe it will have to depend for Proper Nouns or other...

def GetActors_NA(Chunk):#here Chunk refers to type NA, a adjectif playing the role of a noun
    print ("Received the Nounified Adjective \"" + str(Chunk) + "\"")                                                                                                                          
    List = ["TPP" , Chunk]                                                                                                                                               
    print "Added Chunk: " +str(Chunk) + "to the List\n" 
    return List
    #I know I know, this is far from perfect, but still IMO a good simple place to start
    #Atm all this does is recognize adjectives that play the role of nouns as third person plural substitutes
    #it returns them in their new fancy data structure

def GetActors_P(Chunk):
    print ("Received the Pronoun \"" +str(Chunk) + "\"")
    List = []
    Types = ["FPS","SPS","TPSM","TPSF","TPSN","FPP","SPP","TPP"]
    for index in range(0,len(Types)-1):
        if(Chunk[0][0].lower() in PronounTable.PronounList[index]):
            print ("Got A Pronoun of type " +Types[index])
            List.append([Types[index],"PP"])
    
    return List
def GetActors_GON(Chunk):
    List = []
    for index in range(0, len(Chunk)):
        SubChunk = Chunk[index]
   
        List = GetActors_ALL(SubChunk) + List
        print "Got Actors in the SubChunk, This is the new List"
        print List
        #This part enables recurrency, so that an Group of Nouns within a Group Of Nouns Doesnt give an error
        #Basically re analyze everything within the GON

    print "Analysing every SubChunk to see whether its First person plural, second or third"
    for SubChunk in List:
        if((SubChunk[0] == "FPS") or (SubChunk[0] == "FPP")):
            print "Received First Person Pronoun, Returning A First Person Plural Chunk"
            List.insert(0,["FPP",Chunk])
            return List
        elif((SubChunk[0] == "SPS") or (SubChunk[0] == "SPP")):
            print "Received Second Person Pronoun, Returning A Second Person Plural Chunk"
            List.insert(0,["SPP",Chunk])
            return List
      
    print "No First or Second Personal Pronouns detected, thus Returning a Third Person Plural Chunk"
    print "Here is the Chunk"
    print Chunk
    print "Here is the List"
    print List
    List.insert(0,["TPP",Chunk])
    return List

def GetActors_ALL(Chunk):
    List = []
    print "Within Get Actors All, Checking Chunk type"
    print Chunk
    if(type(Chunk) != tuple):
        if(Chunk.label() == "N"):  
            print "Got a Chunk of type Noun, adding to the beginning of the list..."
            List = GetActors_N(Chunk) + List
            print "Added stuff to the List From the Noun"
            print Chunk

        elif(Chunk.label() == "NA"):
            print "Got a Chunk of type Nounified Adjective, adding to the beginning of the list..."
            List = GetActors_NA(Chunk) + List
            print "Added stuff to the List From the Nounified Adjective"
            print Chunk

        elif(Chunk.label() == "WORDS_WITH_COMA"):   
            print "Got a Chunk of type Word with Coma, adding to the beginning of the list..."
            List = GetActors_ALL(Chunk[0]) + List
            print "Added stuff to the List From the Words with Coma"
            print Chunk

        elif(Chunk.label() == "GROUP_OF_NOUNS"):
            print "Got a Chunk of type Group of Nouns, adding to the beginning of the list..."
            List = GetActors_GON(Chunk) + List
            print "Added stuff to the List From the Group of Nouns"
            print Chunk
        elif(Chunk.label() == "P"):
            print "Got a Chunk of type Pronoun, adding to the beginning of the list..."
            List = GetActors_P(Chunk) + List

    print "Done in getActors all!"
    print "Here is the New List "
    print List
    return List

def GetActors(Chunk,mentioned_people):
    print "Analyzing this Chunk in GetActors"
    print Chunk
    List = GetActors_ALL(Chunk)
    print "Got Stuff From Analysing "
    print List
    print len(List)
    index = 0
    for Iterations in range(0,len(List)):
        print index
        print List[index]
        if List[index][1] == "PP":
            print "Element Removed as it was a pronoun"
            List.pop(index)
            index += -1
        index += 1

    if(len(List) == 0):
        return mentioned_people

    mentioned_people = SetPersonalPronoun(List[0],mentioned_people)
    RefferedPronouns = [["FPS",0],["SPS",0],["TPSM",0],["TPSF",0],["TPSN",0],["FPP",0],["SPP",0],["TPP",0]]
    for index in range(0,len(List)):
        for PronounIndex in range(0,len(RefferedPronouns)):
            if (RefferedPronouns[PronounIndex][0] == List[index][0]):
                RefferedPronouns[PronounIndex][1] += 1

    print "\nHere are the number of times each type of pronoun has been referenced"
    print RefferedPronouns
    for index in range(1,len(List)):
        for PronounIndex in range(0,len(RefferedPronouns)):
            if (RefferedPronouns[PronounIndex][0] == List[index][0]) and (RefferedPronouns[PronounIndex][1] == 1):
                print "Setting Up Pronoun from List Because it is the best Option"
                mentioned_people = SetPersonalPronoun(List[index],mentioned_people)
    print List
    return mentioned_people

    

def GetRidOfPronouns(structured_sentence,mentioned_people):
    List = []
    for index in range(0, len(structured_sentence)):
        Chunk = structured_sentence[index]
        print Chunk

        print "Replacing Pronouns in Chunk : " +str(Chunk)
        structured_sentence[index] = ReplacePronouns(Chunk,mentioned_people)
        Chunk = structured_sentence[index]                                                                                                                                                                 
        print "Analysing Chunk : " + str(Chunk) + " for pronouns"
        mentioned_people = GetActors(Chunk,mentioned_people)
    print "Finished Substituting Pronouns "
    print mentioned_people.People
    print structured_sentence
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
                #result = GetActorsAndReplacePronouns(result,mentioned_people)
                GetRidOfPronouns(result,mentioned_people)
                ImportantWords.append(result)
                return ImportantWords
       	except Exception as e:
		print(str(e))
print("Input Text")
text = raw_input("")
returnImportantWords(text)
