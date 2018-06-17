import pickle

print "add time marker"
marker = raw_input("")
print "is this correct? y/n"
command = raw_input("")
if(command == "y") or (command == "yes"): 
    data = []
    with open('timemarkers.pckl',"rb") as f:
        try:
            data = pickle.load(f)
        except Exception as e:
            print(str(e))
    data.append(marker)
    with open('timemarkers.pckl', 'wb') as f:
        pickle.dump(data, f)
        f.close()
    print "done!"
else:
    print "sorry"
