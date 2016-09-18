namePool = []
top200names = []

def filterName(name):
    #get rid of: U.,C., of, at, in, for, and
    banned = {"of", "at", "in", "for", "and"}
    
    name = [x.lower() for x in name]
    
    filtered = []
    for part in name:
        if ',' in part:
            part = part.replace(',','')
        if part == "c.":
            filtered.append("college")
        elif part == "u.":
            filtered.append("university")
        elif part not in banned:
            filtered.append(part)
    
    return tuple(filtered)
    
    pass

def readReasearchExpenseInfo():
    global namePool
    
    fileName  = "Pages/ResearchExpenditure/" + "ResearchExpensesPlainText.txt"
    
    fp = open(fileName,"r")
    for i, line in enumerate(fp):
        if (i<3):
            continue
        line = line.split()
        
        #find name
        #last ten fields are for data. The rest is name
        name = line[:-10] 
        
        #find 2014 expenditure
        expense = line[len(line)-1]
        namePool.append((filterName(name), expense))
    pass
    
def findMatchingName(name): 
    global namePool
    #print(len(namePool))
    
    name = name.lower()
    if '#' in name:
        name = name.replace('#',' ')
    
    max = 0
    res = []
    resExpense = ""
    nameSet = set(name.split())
    
    for element in namePool:
        candidate = element[0]
        candidateSet = set(candidate)
        commonSet = nameSet & candidateSet
        commonList = list(commonSet)
        coefficient = len(commonList)/len(candidate)
        if coefficient == 1:
            max = coefficient
            res = [candidate]
            resExpense = element[1]
        elif coefficient > max:
            max = coefficient
            res = [candidate]
            resExpense = element[1]
            #print(res)
        elif coefficient == max:
            res.append(candidate)
            #print(res)
        
    if len(res) == 1:
        return (res,resExpense)
    else:
        return (None,"0")
        
    pass

def matchUniversityNames1():
    global top200names 

    #first load the record of the top 200 unis
    fileName = "Results/result_combined.txt"
    fp = open(fileName,"r",encoding = "utf8")
    for line in fp:
        top200names.append(line.split("|")[0])
    fp.close()
    
    fp1 = open("test.txt","w",encoding="utf8")
    matchFound = 0
    #now go through each of the names.     
    for name in top200names:
        print(name)
        match,matchExpense = findMatchingName(name)
        if match is not None:
            matchList = [" ".join(list(element)) for element in match]
            fp1.write(name + " matches with -> " + ",".join(matchList) + " -> " + matchExpense + "\n")
            matchFound += 1
        else:
            fp1.write(name + " matches with -> " + "None" + "\n")
    fp1.close()
    print("matchFound: ",matchFound)
    
def matchUniversityNames():
    global top200names 

    #first load the name of the top 200 unis
    fileName = "Results/result_combined.txt"
    fp = open(fileName,"r",encoding = "utf8")
    for line in fp:
        top200names.append(line.split("|"))
    fp.close()
    
    fp1 = open("Results/result_with_endowment_researchExpenses.txt","w",encoding="utf8")
    fp1.write("Rank | Name | Tuition | Endowment | Academic staff | Students | Undergraduates | Postgraduates | 2014 research spending (thousands) \n")
    
    matchFound = 0
    #now go through each of the names.     
    for entry in top200names:
        if len(entry) < 10:
            continue
        #fp1.write("|".join(entry) + "\n")
        name = entry[3].strip("\n\t ")
        rank = entry[0].strip("\n\t ")
        tuition = entry[5].strip("\n\t ")
        endowment = entry[6].strip("\n\t ")
        academicStaff = entry[7].strip("\n\t ")
        students = entry[8].strip("\n\t ")
        undergraduates = entry[9].strip("\n\t ")
        postgraduates = entry[10].strip("\n\t ")
        print(name)
        
        match,researchExpense = findMatchingName(name)
        if match is not None:
            #these line were to verify if a correct match was done 
            #matchList = [" ".join(list(element)) for element in match]
            #fp1.write(name + " matches with -> " + ",".join(matchList) + " -> " + matchExpense + "\n")
            
            
            matchFound += 1
        else:
            #fp1.write(name + " matches with -> " + "None" + "\n")
            pass
        
        #combine all info
        #we need rank, name, tuition, endowment, academic staff, students, undergraduates, postgraduates, research spending    
        tempStr = rank + "|" + name + "|" + tuition + "|" + endowment + "|" + academicStaff + "|" + students + "|" + undergraduates + "|" + postgraduates + "|" + researchExpense + "\n"
        
        fp1.write(tempStr)
            
    fp1.close()
    #print("matchFound: ",matchFound)
    



    
readReasearchExpenseInfo()
matchUniversityNames()
print("Hello World!")