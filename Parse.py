#Jeff Haak
import copy
import MySQLdb
#import re
#import urllib
# Open database connection
# execute SQL query using execute() method.
#SQL = "TRUNCATE " + mySQLQuarters
#cursor.execute(SQL)

###########################################################
################## TO DO/ Other Points ####################
###########################################################
#Make new script for scrapeing later
#Make new script for proffessor tables later
###########################################################

#Dont Use here
def scrapeReg(courseNumber):
    site = "http://register.rit.edu/courseSchedule/" + str(courseNumber)
    data = urllib.urlopen(site)
    html = data.readlines()
    data.close()
    
    matcher = re.compile('<td colspan="2" class="bodyTd">')
    theLines = []
    for lines in html:
        if matcher.search(lines):
            theLines.append(lines)
            
    #These lines weed out the parts that are not the physical description        
    theLine = theLines[1].split("\">")
    theLine = theLine[1].split("</td")
    return theLine[0]

def main():
    #MySQL Connection Info
    #pass info
    mySQLDatabase = "picat"
    #Tables
    mySQLTimes = "timeclassrel"
    mySQLSections = "sections"
    mySQLQuarters = "quarters"
	
    #Quarters Table
    ##########################################################################
    #[Quarter: "20101", Description: "20101 - Fall 2010-2011", Address: "20101/", 
    #    startDate: "2010-09-06", endDate: "2010-11-20"]
    quarter = [] 
    quarters = []
    usedQuarters = [] #used so that there arnt duplicats of a quarter in the DB
    ##########################################################################
    
    #Sections Table
    ##########################################################################
    #[UID: "01013010220101", Quarter: "20101", College: "01", Discipline: "0101", 
    #Course: "0101301", Section: "02", NotesExist: "", Credits: "4",  Notes: Cant Find, 
    #SeatsFull: "23", SeatsAvail: "40", Status: Cant Find, KillBit: Cant Find]
    course = []
    courses = []
    usedCourses = []
    uniqueCourse = []
    ##########################################################################
    
    #TimeClassRel Table
    ##########################################################################
    #[Class = "01013010220101", BeginHour = "08", BeginMin = "00", EndHour = "09",\
    # EndMin = "50" Days = "2", bldg = "LOW(12)", Room = "3115"]
    timeClass = []
    timeClasses = []
    notDone = True
    ##########################################################################
    count = 1
    for line in open("Flatfile.txt"):
        line = line.strip()
        line = line.split("|")
        
        #Quarters Table
        if line[0] not in usedQuarters:
            if line[0][-1] == "1":
                nextYear = int(line[0][:4]) + 1 
                descrip = str(line[0]) + " - Fall " + str(line[0][:4]) + "-" + str(nextYear) 
            elif line[0][-1] == "2":
                nextYear = int(line[0][:4]) + 1 
                descrip = str(line[0]) + " - Winter " + str(line[0][:4]) + "-" + str(nextYear) 
            elif line[0][-1] == "3":
                nextYear = int(line[0][:4]) + 1 
                descrip = str(line[0]) + " - Spring " + str(line[0][:4]) + "-" + str(nextYear) 
            elif line[0][-1] == "4":
                nextYear = int(line[0][:4]) + 1 
                descrip = str(line[0]) + " - Summer " + str(line[0][:4]) + "-" + str(nextYear) 
            
            #Address Field
            address = str(line[0]) + "/"
            #start:
            start = line[3][:4] + "-" + line[3][4:6] + "-" + line[3][6:8]
            #end:
            end = line[4][:4] + "-" + line[4][4:6] + "-" + line[4][6:8]
            
            quarter = [line[0], descrip, address, start, end]
            quarters.append(quarter)
            usedQuarters.append(line[0])
		
        #Sections Table, TimeClassRel
        courseUID = str(line[1]) + str(line[0])
        if courseUID not in usedCourses:
        #Sections Table
        #[UID: "01013010220101", Quarter: "20101", College: "01", Discipline: "0101", 
        #Course: "0101301", Section: "02", NotesExist: "", Credits: "4",  Notes: Cant Find, 
        #SeatsFull: "23", SeatsAvail: "40", Status: Cant Find, KillBit: Cant Find]
            college = line[1][:2]
            discipl = line[1][:4]
            courseNum = line[1][:7]
            section = line[1][7:9]
            notesExist = line[19]
            credits = line[11]
            notes = "No Course Description Available At This Time"
            seatsFull = line[13]
            totalSeats = line[12]
            status = "1"
            killBit = "0"
            course = [courseUID, line[0], college, discipl, courseNum, section, notesExist, \
                      credits, notes, seatsFull, totalSeats, status, killBit]
            courses.append(course)
                    
            #TimeClassRel Table
            #[Class = "01013010220101", BeginHour = "08", BeginMin = "00", EndHour = "09",\
            # EndMin = "50" Days = "2", bldg = "LOW(12)", Room = "3115"]
            #Some classes have classes on more than one day, this loop takes care of that
            times = copy.deepcopy(line[28])
            times = times.split(",")
            while (len(times)-1) > 0:
                day  = times[0]
                times.pop(0)
                bHour = times[0][:2]
                bMin = times[0][2:4]
                times.pop(0)
                eHour = times[0][:2]
                eMin = times[0][2:4]
                times.pop(0)
                bldg = times[0]
                times.pop(0)
                room = times[0]
                times.pop(0)
                
                if day == "1":
                    day = "1"
                elif day == "2":
                    day = "2"
                elif day == "3":
                    day = "4"
                elif day == "4":
                    day = "8"
                elif day == "5":
                    day = "16"
                elif day == "6":
                    day = "32"
                elif day == "7":
                    day = "64"
                
                timeClass = [courseUID, bHour, bMin, eHour, eMin, day, bldg, room]
                timeClasses.append(timeClass)
            usedCourses.append(courseUID)
    		
    #Database Things	
    db = MySQLdb.connect(mySQLHost, mySQLUser, mySQLPass, mySQLDatabase)
    cursor = db.cursor()
    
    #Empty the Quarters Table, then fill it    
    quartersSQL = "TRUNCATE " + mySQLQuarters
    cursor.execute(quartersSQL)	
    addQuarter = "INSERT INTO " + mySQLQuarters + " (uid, description, address, startdate, enddate) VALUES (%s, '%s', '%s', '%s', '%s');"
    for j in quarters: 
        if cursor.execute(addQuarter % (str(j[0]), str(j[1]), str(j[2]), str(j[3]), str(j[4]))):
            pass
    print "Quarters are done!"
    #Sends updates to Database
    db.commit()
    
    """"
    #Empty the Sections Table, then fill it    
    sectionsSQL = "TRUNCATE " + mySQLSections
    cursor.execute(sectionsSQL)    
    addSection = "INSERT INTO " + mySQLSections + " (uid, quarter, college, discipline, course, section, notesexist, credits, notes, seatsFull, seatsAvail, status, KillBit) VALUES (%s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"
    for coursage in courses: 
	print(addSection % (str(coursage[0]), str(coursage[1]), str(coursage[2]), str(coursage[3]), str(coursage[4]), str(coursage[5]), str(coursage[6]),str(coursage[7]), str(coursage[8]), str(coursage[9]), str(coursage[10]), str(coursage[11]), str(coursage[12])))
        if cursor.execute(addSection % (str(coursage[0]), str(coursage[1]), str(coursage[2]), str(coursage[3]), str(coursage[4]), str(coursage[5]), str(coursage[6]), str(coursage[7]), str(coursage[8]), str(coursage[9]), str(coursage[10]), str(coursage[11]), str(coursage[12]))):
            pass
    print "Sections are done!"
    #Sends updates to Database
    db.commit()
    """
    
    
    #Empty the Times Table, then fill it    
    TimesSQL = "TRUNCATE " + mySQLTimes
    cursor.execute(TimesSQL)    
    addTimes = "INSERT INTO " + mySQLTimes + " (class, beginhour, beginminute, endhour, endminute, days, bldg, room) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"
    for theTimes in timeClasses: 
        print (addTimes % (str(theTimes[0]), str(theTimes[1]), str(theTimes[2]), str(theTimes[3]), str(theTimes[4]), str(theTimes[5]), str(theTimes[6]), str(theTimes[7])))
        if cursor.execute(addTimes % (str(theTimes[0]), str(theTimes[1]), str(theTimes[2]), str(theTimes[3]), str(theTimes[4]), str(theTimes[5]), str(theTimes[6]), str(theTimes[7]))):
            pass
    print "Times are done!"
    #Sends updates to Database
    db.commit()
    
    
    # disconnect from server
    db.close()

main()
