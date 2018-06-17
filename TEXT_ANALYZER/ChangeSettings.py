import pickle

print "Would You Like To Change a current Setting \nOR Add a New One? c/a"
ChangeOrAdd = raw_input("")
if(ChangeOrAdd == "c"):
    print "Okay, Changing Settings, \nWhat Variable would you like to change?"
    data = {}
    with open('ParsedTextToDataTableSettings.pckl',"rb") as f:
        try:
            data = pickle.load(f)
        except Exception as e:
            print(str(e))
    print data
    command = raw_input("")
    try:
    	if data[command]:
     	    print "Changing Settings for "+command
	    print "Please Input new value, Current is: "+data[command]
	    value = raw_input("")
	    data[command] = value
	    print "Saving To PICKL"
	    with open('ParsedTextToDataTableSettings.pckl', 'wb') as f:
    	        pickle.dump(data, f)
    	        f.close()
    	    print "Done!"
	else:
	    print "Sorry, no variable was found"
    except:
	print"Sorry, no variable was found"
 
elif(ChangeOrAdd == "a"):
    print "Please input the Variable Name"
    VariableName = raw_input("")
    print "Creating Variable, please input value, press Enter for null,\nKnow That It will be Saved As A STRING"
    Value = raw_input("")
    data = {}
    with open('ParsedTextToDataTableSettings.pckl',"rb") as f:
        try:
            data = pickle.load(f)
        except Exception as e:
            print(str(e))
    data[VariableName] = Value
    with open('ParsedTextToDataTableSettings.pckl', 'wb') as f:
        pickle.dump(data, f)
        f.close()
    print "Done!"
else:
    print "sorry"
