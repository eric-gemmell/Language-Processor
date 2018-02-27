import PronounRemover
import SentenceSplitter

print("Welcolme to This Version of Text_Analysis...\n")
print("Please Input the Text You Would Like To Analyse\n")
text = raw_input("")

#text = PronounRemover.Process(text)

print("Here's what we got")
print text

SentenceSplitter.Process(text)
