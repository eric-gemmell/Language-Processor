import MySQLdb
import os
from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords
from nltk.corpus import state_union

#nltk.download("stopwords")
#nltk.download("punkt")
#nltk.download("state_union")
#nltk.download('averaged_perceptron_tagger')

print("Input Text: \n")
text = raw_input("")

def FilteredList (string):
    FilteredString = []
    for w in word_tokenize(string):
        if not (w in set(stopwords.words("english"))):
            FilteredString.append(w)
    return FilteredString


def ImportantWords(all_words):
    PositionInText = 0
    ImportantWords = []
    os.system("clear")

    while (True):
        Input = raw_input("Input Command: ")
        if(Input == "d"):
            if(PositionInText < len(all_words)-1):
                PositionInText += 1
        elif(Input == "a"):
            if(PositionInText > 0):
                PositionInText += -1
        elif(Input == ""):
            if all_words[PositionInText] in ImportantWords:
                ImportantWords.remove(all_words[PositionInText])
                print ("You Have Removed \"" + all_words[PositionInText] + "\" From Your Important Words")
            else:
                ImportantWords.append(all_words[PositionInText])
                print ("You Have Added \"" + all_words[PositionInText] + "\" To Your Important Words")           
        elif(Input == " "):
            SelectingImportantWords = False
            print ImportantWords
            return ImportantWords
            break

        os.system("clear")
        print(all_words)
        print all_words[PositionInText]
        print ImportantWords
        print PositionInText


def InsertData(string,words):
    conn = MySQLdb.connect("127.0.0.1","brain","brain","BRAIN")
    c = conn.cursor()
    c.execute("INSERT INTO TEXTS (TEXT) VALUES (%s)",(string,))
    conn.commit()
    text_ID = c.lastrowid

    words_ID = []	
    for word in words:
        c.execute("SELECT *, COUNT(*) FROM WORDS WHERE WORD = %s GROUP BY WORD",(word,))
        # gets the number of rows affected by the command executed
        row_count = c.rowcount
        if row_count == 0:
            c.execute("INSERT INTO WORDS (WORD) VALUES (%s)",(word,))
            conn.commit()
            words_ID.append(c.lastrowid)

        else:
            ID = c.fetchall()[0][0]
            words_ID.append(ID)

    for ID1 in words_ID:
        for ID2 in words_ID:
            if ID1 != ID2:
                c.execute("SELECT *, COUNT(*) FROM LINKS WHERE FIRST_WORD = %s AND SECOND_WORD = %s GROUP BY FIRST_WORD",(ID1,ID2,))
                # gets the number of rows affected by the command executed
                row_count = c.rowcount
                link_ID = 0
                if row_count == 0:
                    c.execute("INSERT INTO LINKS (FIRST_WORD,SECOND_WORD,STRENGTH) VALUES (%s,%s,%s)",(ID1,ID2,3))
                    conn.commit()
                    link_ID = c.lastrowid
                else:
                    link = c.fetchall()[0]
                    link_ID = link[0]
                    linkStrength = link[3]
                    c.execute("UPDATE LINKS SET STRENGTH = (%s) WHERE LINK_ID = (%s)", (linkStrength+3,link_ID,))
                    conn.commit()
                c.execute("INSERT INTO TEXT_LINKS (LINK_ID,TEXT_ID) VALUES (%s,%s)",(link_ID,text_ID,))

InsertData(text,ImportantWords(FilteredList(text)))	

