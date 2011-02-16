#Jeff Haak
import copy
import MySQLdb
import re
import urllib


def scrapeReg(courseNumber):
    site = "http://register.rit.edu/courseSchedule/" + str(courseNumber)
    data = urllib.urlopen(site)
    html = data.readlines()
    data.close()
    
    matcher = re.compile('<td colspan="2" class="bodyTd">')
    nameMatcher = re.compile('<td class="bodyTd">')
    theLines = []
    nameLines = []
    for lines in html:
        if matcher.search(lines):
            theLines.append(lines)
        if nameMatcher.search(lines):
            nameLines.append(lines)
                
    #These lines weed out the parts that are not the physical description        
    theLine = theLines[1].split("\">")
    theLine = theLine[1].split("</td")
    #Names
    nameLine = nameLines[2]
    nameLine = nameLine.split("\">")
    nameLine = nameLine[1].split("</td")
    name = nameLine[0]    
    
    return [theLine[0], name]

def main():
    #MySQL Connection Info
    mySQLPass = "FeQvtrexWYx6LFUC"
    mySQLHost = "db.csh.rit.edu"
    mySQLUser = "zemon1"
    mySQLDatabase = "picat"
    
    #Tables
    mySQLCourses = "courses"

    #Courses Table
    ##########################################################################
    #[UID: "01013010220101", Quarter: "20101", College: "01", Discipline: "0101", 
    #Course: "0101301", Section: "02", NotesExist: "", Credits: "4",  Notes: Cant Find, 
    #SeatsFull: "23", SeatsAvail: "40", Status: Cant Find, KillBit: Cant Find]
    course = []
    courses = []
    usedCourses = []
    uniqueCourse = []
    ##########################################################################
    
    count = 1
    for line in open("Flatfile.txt"):
        line = line.strip()
        line = line.split("|")
                
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
            #if courseNum not in uniqueCourse:
            #    notesName = scrapeReg(courseNum)
            #    uniqueCourse.append(courseNum)
            description = "N/A"
            name = "N/A"
            notes = ""
            course = [courseNum, college, discipl, name, description, notes]
            print course
            courses.append(course)
            usedCourses.append(courseUID)
    print "Courses Done!!!\n\n\n\n\n\n\n\n\n"        
    #Database Things    
    db = MySQLdb.connect(mySQLHost, mySQLUser, mySQLPass, mySQLDatabase)
    cursor = db.cursor()
    
    #Empty the Quarters Table, then fill it    
    coursesSQL = "TRUNCATE " + mySQLCourses
    cursor.execute(coursesSQL)    
    addCourses = "INSERT INTO " + mySQLCourses + " (uid, discipline, name, description, notes) VALUES ('%s', '%s', '%s', '%s', '%s');"
    for j in courses: 
        if cursor.execute(addCourses % (str(j[0]), str(j[2]), str(j[3]), str(j[4]), str(j[5]))):
            pass
        if count %302 == 0:
            print count
        print count
        count += 1
    print "Courses are done!"
    #Sends updates to Database
    db.commit()

main()