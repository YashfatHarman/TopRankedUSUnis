from urllib.request import urlretrieve
from urllib.error import HTTPError,URLError
from bs4 import BeautifulSoup
import operator
from os import listdir
import pickle
import re

extractedFromUsnews = []
poolOfWikiLinks = {}
linkOfUniWikiPages = {}

folderName = "Pages"
pretext = "https://en.wikipedia.org"

#fetch the pages at first
def fetchPage(url,name):
    try:
        urlretrieve(url, name)
    except HTTPError as e:
        print("Error. Reason: ",e.reason)
        print("quitting ...")
        quit()
    except URLError as e:
        print("Error. Reason: ",e.reason)
        print("quitting ...")
        quit()
    else:
        pass

def stripRankInfo(rankText):
    '''
    sample input:
    #1


    Overall Score: 100 out of 100.    
    '''
    rank = rankText[rankText.find('#')+1:rankText.find('\n',rankText.find('#')+1)]
    if rank == "RNP":   #after 199, ranking is not available. So assigning an arbitrary big value that can be used to ignore it later
        rank = "1000"
    if rank.isdigit() is not True:
        rank = rank[:rank.find("Tie")]
    score = rankText[rankText.find("Score: ")+len("Score: ") : rankText.find(" out")]
    outOf = rankText[rankText.find("out of ") + len("out of ") : rankText.find('.',rankText.find("out of "))]
    return (rank, score, outOf)
    pass
    
def extractTableDataFromRow(row):
    rankElement = row.find("td", {"class" : "v_display_rank"})
    rankInfo = rankElement.get_text().strip("\n\t ")
    rank,score,outOf = stripRankInfo(rankInfo)
    rank = int(rank)

    nameElement = row.find("a", {"class" : "school-name"})
    name = nameElement.get_text().strip("\n\t ")
    
    locationElement = row.find("p", {"class" : "location"})
    location = locationElement.get_text().strip("\n\t ")
    
    tuitionElement = row.find("td", {"class" : "search_tuition_display"})
    tuition = tuitionElement.get_text().strip("\n\t ")
    
    studentsElement = row.find("td", {"class" : "total_all_students"})
    students = studentsElement.get_text().strip("\n\t ")
    
    return (rank, score, outOf, name, location, tuition, students)
    
    pass
    
def extractLinks(name):
    global extractedFromUsnews
    
    #open the file, read it
    fp = open(name, "r", encoding="utf8")
    allText = fp.read()
    fp.close()
    
    #soupify
    soup = BeautifulSoup(allText,"lxml")
    
    
    #we need to extract odd rows and even rows.
    #first row and last row also contain tags odd-row and even-row, so they need not be looked separately. 

    oddRows = soup.find_all("tr", {"class" : "table-row-odd"})
    for row in oddRows:
        info = extractTableDataFromRow(row)
        if info[0] <= 200:   #if rank is not available, then a value of 1000 will be returned as rank
            extractedFromUsnews.append(list(info))
        
    evenRows = soup.find_all("tr", {"class" : "table-row-even"})
    for row in evenRows:
        info = extractTableDataFromRow(row)
        if info[0] <= 200:   #if rank is not available, then a value of 1000 will be returned as rank
            extractedFromUsnews.append(list(info))
    
    extractedFromUsnews.sort(key = operator.itemgetter(0))
    
    
    pass

def extractUSNewsPages():    
    
    #generate urls
    urlsAndNames = []
    url = "http://colleges.usnews.rankingsandreviews.com/best-colleges/rankings/national-universities/data"
    name = "Page1.html"
    urlsAndNames.append((url, name))

    for i in range(2,9): 
        url = "http://colleges.usnews.rankingsandreviews.com/best-colleges/rankings/national-universities/data/page+" + str(i)
        name = "Page" + str(i) + ".html"
        urlsAndNames.append((url, name))

    #fetch and process pages
    folderName = "Pages"
    for tup in urlsAndNames:
        url = tup[0]
        name = folderName + "/" + tup[1]
        #name = tup[1]
        fetchPage(url,name)
        extractLinks(name)
        
    #sort and write in a file
    fp1 = open("Results/result.txt", "w", encoding="utf8")
    for row in extractedFromUsnews:
        first = str(row[0])
        rest = [row[i] for i in range(1,len(row))]
        fp1.write(first + "|" + '|'.join(rest) + "\n")
    fp1.close()
    pass
    
def checkTitleForPattern(title):
    searchStr = "List of colleges and universities in"
    if title is not None and title.find(searchStr) != -1:
        return True
    return False
    
    
def getWikiPageLinkForAllStates():
    #two step parsing needed
    #This page contains links state-wise links for colleges:https://en.wikipedia.org/wiki/Lists_of_American_institutions_of_higher_education
    #Then, each state has an individual page. For example, Florida has this: https://en.wikipedia.org/wiki/Lists_of_American_institutions_of_higher_education
    #From the first page, link for the second levels need to be extracted. Then from the second one, link of wikipage for all the unis can be extracted and saved.
    #Then we can search for any uni we are looking for.
    
    #this function only fetches the top level page, parses it, then fetches state-level pages and saves them in a specific folder.
    
    #fetch the first page
    url = "https://en.wikipedia.org/wiki/Lists_of_American_institutions_of_higher_education" 
    name = folderName + "/" + "StateWiseListOfUnis" + ".html"
    fetchPage(url, name)
    
    #now fetch and extract links for each state
    '''
    we are looking for elements like this:
    <li><a href="/wiki/List_of_colleges_and_universities_in_Alabama" title="List of colleges and universities in Alabama">Alabama</a></li>
    '''
    
    #open the file, read it
    fp = open(name, "r", encoding="utf8")
    allText = fp.read()
    fp.close()
    
    #soupify
    soup = BeautifulSoup(allText,"lxml")
    
    
    statesAndUrl = []
    
    #find all <a> tags whose title falls into a specific pattern
    linkTags = soup.find_all("a", title = checkTitleForPattern)
    for linkTag in linkTags:
        state = linkTag.get_text().strip("\n\t ")
        link = pretext + linkTag["href"] 
        statesAndUrl.append((state,link))
        
    #now bring state-wide pages 
    folderName2 = folderName + "/" + "States"    
    for tup in statesAndUrl:
        name = folderName2 + "/" + tup[0] + ".html"
        url = tup[1]
        fetchPage(url,name)
    
    pass

def hasTitle(title):
    if title is not None:
        return True
    return False    
    
def extractWikiLinksForAllUniversitiesInTheUS():
    #go through the folder "Pages/States"
    #for every file there:
        #get all the university name, and link
        
    global poolOfWikiLinks
    
    folderName2 = "Pages/States"
   
    outfileName = folderName2 + "/links.txt"
    fp2 = open(outfileName, "w", encoding="utf8")
   
    fileNames = [f for f in listdir(folderName2)]
    
    for fileName in fileNames:
        name = folderName2 + "/" + fileName
        fp = open(name, "r", encoding="utf8")
        allText = fp.read()
        fp.close()
        
        soup = BeautifulSoup(allText,"lxml")
        
        '''
        We are looking for something like this:
            <a href="/wiki/Princeton_University" title="Princeton University">Princeton</a>
        The problem is, every wiki page has tons of links and it's almost impossible for us to decide which is an university and which is not.
        Thankfully, we don't need to  generate lists of all the universities in the US.
        So we can save every link in a huge dictionary and then later use that to search for the links for the 200 universities we are interested in.
        '''
        
        linkElements = soup.find_all("a",title=hasTitle)
        
        for linkElement in linkElements:
            title = linkElement["title"]
            url = pretext + linkElement["href"]
            #print(title,url)
            
            if title not in poolOfWikiLinks:
                poolOfWikiLinks[title] = url
            
            fp2.write(title + "|" + url + "\n")
            
    fp2.close()
    
    #let's save the dict as well. Will help in the subsequent runs
    pickleFile = "Pickles/" + "linkPool.p"
    pickle.dump(poolOfWikiLinks, open(pickleFile,"wb") )
    
    pass

def vanishUnicodeDash():
    #its a nuisance. Replace it with a "#"
    #apparently there is a zero-width space as well. Replace that one too.
    
    fileName = "Results/result.txt"
    
    with open(fileName, 'r',encoding="utf8") as content_file:   #this closes the file after the block ends
        content = content_file.read()
    
    content = content.replace(u"\u2014","#")
    content = content.replace(u"\u200b","")
    
    fp = open(fileName,"w",encoding="utf8")
    fp.write(content)
    fp.close()
    
def findWikiPageForTop200Universities():
    global poolOfWikiLinks
    global linkOfUniWikiPages
    
    #load the pool of dictionary 
    pickleFile = "Pickles/" + "linkPool.p"
    poolOfWikiLinks = pickle.load(open(pickleFile,"rb"))

    #now load the list of top 200 unis
    top200Unis = []
    fileName = "Results/result.txt"
    fp = open(fileName,"r",encoding="utf8")
    for line in fp:
        splitted = line.split("|")
        top200Unis.append(splitted[3])
    fp.close()
    
    '''
    Some name contains special characters (usually dash) that makes it impossible to look into the dict.
    In this case, try each of the following:
        - replace the dash with "at"
        - replace the dash with ","
        - replace the dash with "in"
        - replace the dash with a space
        - just take the part upto the dash, ignore the rest
    If none of this work, manual intervention may be needed.
    '''
    #print(len(top200Unis))
    found = 0
    for name in top200Unis: 
        if "#" not in name:
            #proceed normally
            if name in poolOfWikiLinks:
                #print(name, " ---> ", poolOfWikiLinks[name])
                linkOfUniWikiPages[name] = poolOfWikiLinks[name]
                found += 1
            else:
                print(name)
                
        else:
            #special treatment
            newname = name.replace("#", " at ")
            if newname in poolOfWikiLinks:
                #print(newname, " ---> ", poolOfWikiLinks[newname])
                linkOfUniWikiPages[name] = poolOfWikiLinks[newname]
                found += 1
            else:
                newname = name.replace("#", ", ")
                if newname in poolOfWikiLinks:
                    #print(newname, " ---> ", poolOfWikiLinks[newname])
                    linkOfUniWikiPages[name] = poolOfWikiLinks[newname]
                    found += 1
                else:    
                    newname = name.replace("#", " in ")
                    if newname in poolOfWikiLinks:
                        #print(newname, " ---> ", poolOfWikiLinks[newname])
                        linkOfUniWikiPages[name] = poolOfWikiLinks[newname]
                        found += 1
                    else:
                        newname = name.replace("#", " ")
                        if newname in poolOfWikiLinks:
                            #print(newname, " ---> ", poolOfWikiLinks[newname])
                            linkOfUniWikiPages[name] = poolOfWikiLinks[newname]
                            found += 1
                        else:    
                            newname = name[:name.find("#")]
                            if newname in poolOfWikiLinks:
                                #print(newname, " ---> ", poolOfWikiLinks[newname])
                                linkOfUniWikiPages[name] = poolOfWikiLinks[newname]
                                found += 1
                            else:
                                
                                print(name)
                                
    print("Total found: ", found)
    
    #total found 189. So still 203-189 = 14 missing. Let's just put them manually and get done with it. A clever implementation would've been to use google search results instead.
    '''
    These are the ones not found this way:
        University of Wisconsin#Madison
        University of Illinois#Urbana-Champaign
        Rutgers, The State University of New Jersey#New Brunswick
        SUNY College of Environmental Science and Forestry
        University of the Pacific
        University of St. Thomas
        The Catholic University of America
        Rutgers, The State University of New Jersey#Newark
        Missouri University of Science & Technology
        Oklahoma State University
        St. John's University
        Maryville University of St. Louis
        St. Mary's University of Minnesota
        Indiana University-Purdue University#Indianapolis
    '''
    linkOfUniWikiPages["University of Wisconsin#Madison"] = "https://en.wikipedia.org/wiki/University_of_Wisconsin-Madison"
    linkOfUniWikiPages["University of Illinois#Urbana-Champaign"] = "https://en.wikipedia.org/wiki/University_of_Illinois_at_Urbana%E2%80%93Champaign"
    linkOfUniWikiPages["Rutgers, The State University of New Jersey#New Brunswick"] = "https://en.wikipedia.org/wiki/Rutgers_University"    
    linkOfUniWikiPages["SUNY College of Environmental Science and Forestry"] = "https://en.wikipedia.org/wiki/State_University_of_New_York_College_of_Environmental_Science_and_Forestry"    
    linkOfUniWikiPages["University of the Pacific"] = "https://en.wikipedia.org/wiki/University_of_the_Pacific_%28United_States%29"
    linkOfUniWikiPages["University of St. Thomas"] = "https://en.wikipedia.org/wiki/University_of_St._Thomas_%28Minnesota%29"
    linkOfUniWikiPages["The Catholic University of America"] = "https://en.wikipedia.org/wiki/Catholic_University_of_America"
    linkOfUniWikiPages["Rutgers, The State University of New Jersey#Newark"] = "https://en.wikipedia.org/wiki/Rutgers_University%E2%80%93Newark"
    linkOfUniWikiPages["Missouri University of Science & Technology"] = "https://en.wikipedia.org/wiki/Missouri_University_of_Science_and_Technology"
    linkOfUniWikiPages["Oklahoma State University"] = "https://en.wikipedia.org/wiki/Oklahoma_State_University%E2%80%93Stillwater"
    linkOfUniWikiPages["St. John's University"] = "https://en.wikipedia.org/wiki/St._John's_University_%28New_York_City%29"
    linkOfUniWikiPages["Maryville University of St. Louis"] = "https://en.wikipedia.org/wiki/Maryville_University"
    linkOfUniWikiPages["St. Mary's University of Minnesota"] = "https://en.wikipedia.org/wiki/Saint_Mary's_University_of_Minnesota"
    linkOfUniWikiPages["Indiana University-Purdue University#Indianapolis"] = "https://en.wikipedia.org/wiki/Indiana_University_%E2%80%93_Purdue_University_Indianapolis"
    
    fileName = "Results/top200uniLinks.txt"
    fp2 = open(fileName,"w",encoding="utf8")
    for element in sorted(linkOfUniWikiPages.items()):
        fp2.write(element[0] + "|" + element[1] + "\n")
    fp2.close()
    
    #let's pickle the link dictionary as well
    pickleFile = "Pickles/" + "top200uniLinks.p"
    pickle.dump(linkOfUniWikiPages, open(pickleFile,"wb") )
    
    pass

def fetchWikiPagesForTop200Unis():
    pickleFile = "Pickles/" + "top200uniLinks.p"
    linkOfUniWikiPages = pickle.load(open(pickleFile,"rb"))
    
    for element in linkOfUniWikiPages.items():
        name = "Pages/Unis/" + element[0] + ".html"
        url = element[1]  
        print(name)
        if name == "Pages/Unis/University of Wisconsin#Madison.html": #for some reason this kept crashing. So skipping. Will probably just copy manually.
            print("skipping ..." )
        else:
            fetchPage(url,name)
        
    pass
 
def extractEndowmentAndOtherInfo(name):
    #parse the wiki page of an uni and get the info from the top right hand box
    
    '''
    the box is under a table :
        #<table class="infobox vcard" style="width:22em">
    Grab this box, then look for individual fields. Easy.
    '''
    
    #go to folder, open the file, read
    fileName = "Pages/Unis/" + name + ".html"
    fp = open(fileName,"r",encoding = "utf8" )
    allText = fp.read()
    fp.close()
    
    #soupify
    soup = BeautifulSoup(allText,"lxml")
    
    #get the table
    table = soup.find("table", {"class" : "infobox"})
        
    '''
    Individual fields are tricky. For example for Endowment, there is no unique identifier for the tag. One idea is to parse through tag, its parent, then parent's sibling, this way. Alternative is, just take all the text under <tr> tag and then look for keywords like "Endowment", "Academic staff" etc. within this text. Messy.
    
    There may be some stuff missing as well. So need to handle for those.
    '''
    
    #look for Endowment, Academic staff, Students, Undergraduates, Postgraduates
    endowmentText = ""
    academicStaffText = ""
    studentsText = ""
    undergraduatesText = ""
    postgraduatesText = ""
    rows = table.find_all("tr")
    for row in rows:
        rowData = row.get_text()
        
        if "Endowment" in rowData:
            endowmentText = rowData
        elif "Academic staff" in rowData:
            academicStaffText = rowData
        elif "Students" in rowData:
            studentsText = rowData
        elif "Undergraduates" in rowData:
            undergraduatesText = rowData
        elif "Postgraduates" in rowData:
            postgraduatesText = rowData
    
    #print(endowmentText,academicStaffText,studentsText,undergraduatesText,postgraduatesText)
    
    if endowmentText != "":
        endowment = endowmentText[endowmentText.find("$")+1 : endowmentText.find("[")] 
    else:
        endowment = "0"

    pattern = r'[\d,]+'
    p = re.compile(pattern)
    
    if academicStaffText != "":
        match = p.search(academicStaffText)
        if match is not None:
            academicStaff = academicStaffText[match.span()[0]:match.span()[1]]
        else:
            academicStaff = "0"
    else:
        academicStaff = "0"
      
    if studentsText != "":
        match = p.search(studentsText)
        if match is not None:
            students = studentsText[match.span()[0]:match.span()[1]]
        else:
            students = "0"
    else:
        students = "0"
    
    if undergraduatesText != "":
        match = p.search(undergraduatesText)
        if match is not None:
            undergraduates = undergraduatesText[match.span()[0]:match.span()[1]]
        else:
            undergraduates = "0"
    else:
        undergraduates = "0"
    
    if postgraduatesText != "":
        match = p.search(postgraduatesText)
        if match is not None:
            postgraduates = postgraduatesText[match.span()[0]:match.span()[1]]
        else:
            postgraduates = "0"
    else:
        postgraduates = "0"
    
    return (endowment,academicStaff,students,undergraduates,postgraduates)
    
    pass

def combineUSNewsAndWikiPageInfo():
    #go through result.txt
    #Each line contains USNews info for a university
    #Get the wiki page for that university
    #extract necessary info from wiki
    #combine this info with the older ones
    #write it into a new file
    
    fileName = "Results/" + "result.txt"
    fp = open(fileName, "r", encoding = "utf8")
    
    outfileName = "Results/" + "result_combined.txt"
    fp1 = open(outfileName, "w", encoding = "utf8") 
    
    combinedRecords = []
    
    for line in fp:
        #each line contains: rank|points|outOf|school-name|Location|tuition|students
        records = line.split("|")
        
        newRecords = records[:len(records)-1] #excluding total students. That info is available in the wiki page, so keeping that one.
        name = records[3]
        
        if name == "University of Wisconsin#Madison":
            #this is a problem child
            pass
        else:
            #find the corresponding wiki page
            endowment,academicStaff,students,undergraduates,postgraduates = extractEndowmentAndOtherInfo(name)
            
            newRecords.extend(list((endowment,academicStaff,students,undergraduates,postgraduates)))
            fp1.write('|'.join(newRecords) + "\n")
            combinedRecords.append(newRecords)
            
    fp1.close()
    fp.close()
    
    #why not make a pickle too?
    pickleFile = "Pickles/" + "USNewsAndWikiInfoCombined.p"
    pickle.dump(combinedRecords, open(pickleFile,"wb") )
    
    pass
    
#extractUSNewsPages()
#getWikiPageLinkForAllStates()
#extractWikiLinksForAllUniversitiesInTheUS()
#findWikiPageForTop200Universities()
#vanishUnicodeDash()
#fetchWikiPagesForTop200Unis()
#combineUSNewsAndWikiPageInfo()

print("Hello World")
