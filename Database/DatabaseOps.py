#read the cleaned result file, read each record, and put them in a database
#For the time being, let's only consider SQLite Database. Hopefully will expand to PostGres later.

#Fields in the table will be Rank(int), Name(text), City(text), State(text), Endowments(float), Academic Staff(int), Students(int), UnderGraduates(int), PostGraduates(int), 2014 research Spending(float)

import sqlite3

def createTable():
    conn = sqlite3.connect("USUnis.db")
    
    if conn is None:
        print("Error opening database ...")
        return False
    
    #create Table 
    query = '''CREATE table UniRecords 
        (Rank int,
        Name text PRIMARY KEY NOT NULL,
        City char(25),        
        State char(2),
        Endowments float,
        AcademicStaff int,
        Students int,
        UnderGraduates int, 
        PostGraduates int,
        ResearchSpending2014 float);'''
        
    conn.execute(query)
    conn.close()
    
def populateTable():
    inputFile = "result_with_endowment_researchExpenses_cleaned.txt"
    
    fp = open(inputFile,"r")
    records = []
    for line in fp:
        if line[0] == 'R':  #to skip the header line
            continue
        fields = line.strip().split(",")
        
        for field in fields:
            if "#" in field:
                field = field.replace("#",", ")
        
        records.append(fields)
        if len(fields) != 10:
            print(fields, len(fields))
    fp.close()
    
    #insert records into the table
    conn = sqlite3.connect("USUnis.db")
    conn.executemany("INSERT INTO UniRecords VALUES (?,?,?,?,?,?,?,?,?,?)",records)
    conn.commit()
    conn.close()
    
def readFromTable():
    conn = sqlite3.connect("USUnis.db")
    cursor = conn.execute("SELECT * FROM UniRecords WHERE State='FL'")
    
    for row in cursor:
        print(row)
        
    conn.close()
 
print("Hello World!")
#createTable()
#populateTable()
readFromTable()