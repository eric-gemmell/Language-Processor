'''
THIS IS NOT FUNCTIONAL AT THE MOMENT
'''
import SentenceSplitter
import pickle
from nltk.tree import Tree
import Tkinter

def Save(sentence,structured_sentence):
    complete_data = []
    with open('testdata.pckl',"rb") as f:
        try:
            complete_data = pickle.load(f)
        except Exception as e:
            print(str(e)) 
    complete_data.append([sentence,structured_sentence])
    with open('testdata.pckl', 'wb') as f:
        pickle.dump(complete_data, f)
        f.close()

def LoadData():
    complete_data = []
    with open('testdata.pckl', "rb") as f:
        try:
            complete_data = pickle.load(f)
        except Exception as e:
            print(str(e))
    return complete_data


print("test or add? t/a")

command = raw_input("")
if (command == "add") or (command == "a") :
    print "Please input text to analyse"
    text = raw_input("")
    structured_sentences = SentenceSplitter.Process(text)
    sentences = SentenceSplitter.MakeIndividualSentences(text)

    for structured_sentence in structured_sentences:
        structured_sentence.draw()

    print("are these good parses? y/n")
    command = raw_input("")
    if(command == "yes") or (command == "y"):
        for a in range(0,len(sentences)):
            print "Saving Parse"
            Save(sentences[a],structured_sentences[a])
    else:
        print "Sorry"

elif(command == "test") or (command == "t"):
    print "Testing..."
    number_error = 0
    number_correct = 0
    for sentence_pair in LoadData():
        structured_sentence = SentenceSplitter.Process(sentence_pair[0])
        structured_sentence[0].draw()
        #sentence_pair[1][0].draw()

