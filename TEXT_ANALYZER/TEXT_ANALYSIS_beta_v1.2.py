import PronounRemover
import SentenceSplitter
import Tkinter
import GenerateDataTree

print("Welcolme to This Version of Text_Analysis...\n")
print("Please Input the Text You Would Like To Analyse\n")
text = raw_input("")

#text = PronounRemover.Process(text)

print("Here's what we got\n")

structured_sentences = SentenceSplitter.Process(text)
#print structured_sentences
#for structured_sentence in structured_sentences:
#    structured_sentence.draw()

print("Generating Data Tree!")
GenerateDataTree.Process(structured_sentences,text)

