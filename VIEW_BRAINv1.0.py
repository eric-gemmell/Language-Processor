import MySQLdb
import os

def GetRequest():
    print("Enter Stimulus to Receive a Response")
    word = raw_input("")
    Response(word)

def Response(stimulus):
    conn = MySQLdb.connect("127.0.0.1","brain","brain","BRAIN")
    c = conn.cursor()
    c.execute("SELECT * FROM WORDS WHERE WORD = %s GROUP BY WORD", (stimulus,))
    row_count = c.rowcount
    if row_count == 0:
        print "Sorry There Was No Response to that Stimulus..."
    else :
        print "\n\nCollecting Data..."
        stimulus_ID = c.fetchall()[0][0]
        c.execute("SELECT * FROM LINKS WHERE FIRST_WORD = %s",(stimulus_ID,))
        for link in c.fetchall():
            link_ID = link[0]
            link_strength = link[3]
            linked_word_ID = link[2]
            c.execute("SELECT * FROM WORDS WHERE WORD_ID = %s",(linked_word_ID,))
            print (c.fetchall()[0][1],link_strength)

    GetRequest()       

GetRequest()    
