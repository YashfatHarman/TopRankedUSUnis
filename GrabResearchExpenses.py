import operator

namePool = []
top200names = []
records = []
intRecords = []


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
        location = entry[4].strip("\n\t ")
        city = location[:location.find(',')]
        state = location[location.find(',')+2:] 
        
        tuition = entry[5].strip("\n\t ")
        endowment = entry[6].strip("\n\t ")
        academicStaff = entry[7].strip("\n\t ")
        students = entry[8].strip("\n\t ")
        undergraduates = entry[9].strip("\n\t ")
        postgraduates = entry[10].strip("\n\t ")
        #print(name, city, state)
        
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
        tempStr = rank + "|" + name + "|" + city + "|" + state + "|" + tuition + "|" + endowment + "|" + academicStaff + "|" + students + "|" + undergraduates + "|" + postgraduates + "|" + researchExpense + "\n"
        
        fp1.write(tempStr)
            
    fp1.close()
    #print("matchFound: ",matchFound)
   
def removeCommas(str):
    tempStr = [c for c in str if c.isdigit()]
    num = int("".join(tempStr))
    return num
    pass
    
def removeUnwantedChars(str):
    tempStr = [c for c in str if c.isdigit() or c == '.']
    num = float("".join(tempStr))
    return num
    pass
   
def processEndowment(endowment):
    #22.723 billion (2015)
    #check for ()
    if endowment == "0":
        return 0
    else:
        if '(' in endowment:
            endowment = endowment[:endowment.find('(')]
        
        value = endowment[:endowment.find(' ')]
        
        #print(endowment,value)
        floatValue = removeUnwantedChars(value) 
        #print(floatValue)
         
        if 'b' in endowment or 'B' in endowment:
            floatValue = floatValue * 1000 
        elif 'm' not in endowment and 'M' not in endowment:
            floatValue = floatValue / 1000000
         
        #print(endowment,value,floatValue)
        
    return floatValue
    pass
   
def processNumbers():   
    global records
    global intRecords
    
    fileName = "Results/result_with_endowment_researchExpenses.txt"
    fp = open(fileName,"r",encoding = "utf8")
    
    for i, line in enumerate(fp):
        if i==0:
            continue
        records.append(line.split("|"))
    fp.close()
    
    for record in records:
        rank = record[0]
        intRank = int(rank)
        
        name = record[1]
        city = record[2]
        state = record[3]
        
        researchExpense = record[10]
        intResearchExpense = removeCommas(researchExpense)
       
        academicStaff = record[6]
        intAcademicStaff = removeCommas(academicStaff)
        
        students = record[7]
        intStudents = removeCommas(students)
        
        undergraduates = record[8]
        intundergraduates = removeCommas(undergraduates)
        
        postgraduates = record[9]
        intpostgraduates = removeCommas(postgraduates)
                
        endowments = record[5]
        floatEndowments = processEndowment(endowments)
        #print(floatEndowments)
        
        #rank, name, city, state, endowment, academicStaff, students, undergraduates, postgraduates, researchExpense
        print(intRank,name, city, state, floatEndowments,intAcademicStaff, intStudents, intundergraduates,intpostgraduates,intResearchExpense)
        
        intRecords.append((intRank,name, city, state, floatEndowments,intAcademicStaff, intStudents, intundergraduates,intpostgraduates,intResearchExpense))
        
    #save the formatted and "integered" values into yet another output file
    fileName2 = "Results/result_with_endowment_researchExpenses_cleaned.txt"
    fp2 = open(fileName2,"w+",encoding = "utf8")
    
    fp2.write("Rank,Name,Tuition,Endowment,Academic staff,Students,Undergraduates,Postgraduates,2014 research spending (thousands)\n")
    for record in intRecords:
        tempStr = ",".join([str(item) for item in record]) + "\n"
        fp2.write(tempStr)
    
    fp2.close() 
    
    pass
    
def calculateMSE(idx):
    #first check research spending
    global intRecords
    
    #sort based on researchExpense
    array2 = intRecords[:]
    array2.sort(key=operator.itemgetter(idx),reverse = True)
    
    MSE = 0.0
    for i in range(len(intRecords)):
        name1 = intRecords[i][1]
        rank1 = intRecords[i][0]
        #print(name1,rank1)
        for j in range(len(array2)):
            name2 = array2[j][1]
            if name1 == name2:
                rank2 = j
                break
        #print(name2,rank2)  
        diff = rank1-rank2 
        #print(diff)
        #print(diff*diff)
        MSE += (rank1 - rank2) * (rank1 - rank2)
    
    #print(MSE)
    return MSE
    
#readReasearchExpenseInfo()
#matchUniversityNames()

processNumbers()
'''
MSEresearchEx = calculateMSE(9)
print("Research Expense:",MSEresearchEx)

MSEendowments = calculateMSE(4)
print("Endowment:",MSEendowments)

MSEacademicStaff = calculateMSE(5)
print("Academic staff:",MSEacademicStaff)

MSEStudents = calculateMSE(6)
print("Students:",MSEStudents)

MSEundergrads = calculateMSE(7)
print("Undergrads:",MSEundergrads)

MSEpostgrads = calculateMSE(8)
print("Postgrads:",MSEpostgrads)
'''
print("Hello World!")
