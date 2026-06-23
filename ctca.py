import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Cameras:", f"{row[0]:,}")
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Speed Cameras:", f"{row[0]:,}")
    dbCursor.execute("SELECT COUNT(Num_Violations) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Camera Violation Entries:", f"{row[0]:,}")
    dbCursor.execute("SELECT COUNT(Num_Violations) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Speed Camera Violation Entries:", f"{row[0]:,}")
    dbCursor.execute("SELECT Violation_Date FROM RedViolations ORDER BY Violation_Date ASC LIMIT 1;")
    rowa = dbCursor.fetchone()
    dbCursor.execute("SELECT Violation_Date FROM RedViolations ORDER BY Violation_Date DESC LIMIT 1;")
    rowb = dbCursor.fetchone()
    print("  Range of Dates in the Database:",rowa[0], "-", rowb[0])
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Red Light Camera Violations:", f"{row[0]:,}")
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Speed Camera Violations:", f"{row[0]:,}")

##################################################################  
#
# commandOne
#
# Given a connection to the database and name of an intersection, executes an
# SQL querie to retrieve and output intersection
#
def commandOne(dbConn,userInput):
    dbCursor = dbConn.cursor()
    sql = """
    SELECT Intersection_ID, Intersection
    FROM Intersections
    WHERE Intersection LIKE ?
    ORDER BY Intersection ASC;
    """
    dbCursor.execute(sql,(userInput,))
    rows = dbCursor.fetchall()
    if(len(rows)==0):
        print("No intersections matching that name were found.")
    for row in rows:
        print(row[0], " : ", row[1])

##################################################################  
#
# commandTwo
#
# Given a connection to the database and name of an intersection, executes two
# SQL queries to retrieve and output all the cameras at the intersection 
#
def commandTwo(dbConn,userInput):
    dbCursor = dbConn.cursor()
    sql = """
    SELECT Camera_ID, Address
    FROM RedCameras
    JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
    WHERE Intersection = ?
    ORDER BY Camera_ID;
    """
    dbCursor.execute(sql,(userInput,))
    rows = dbCursor.fetchall()
    if(len(rows)==0):
        print()
        print("No red light cameras found at that intersection.")
    else:
        print()
        print("Red Light Cameras:")
        for row in rows:
            print("  ", row[0], " : ", row[1])

    print()
    
    sql = """
    SELECT Camera_ID, Address
    FROM SpeedCameras
    JOIN Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
    WHERE Intersection = ?
    ORDER BY Camera_ID;
    """
    dbCursor.execute(sql,(userInput,))
    rows = dbCursor.fetchall()
    if(len(rows)==0):
        print("No speed cameras found at that intersection.")
    else:
        print("Speed Cameras:")
        for row in rows:
            print("  ", row[0], " : ", row[1])

##################################################################  
#
# commandThree
#
# Given a connection to the database and a date of format: YYYY-MM-DD, executes an
# SQL querie to retrieve and output the percentages of violations on that date
#
def commandThree(dbConn,userInput):
    dbCursor = dbConn.cursor()
    sql = """
    SELECT
    (SELECT SUM(Num_Violations) FROM RedViolations WHERE Violation_Date = ?) AS RedViolations,
    (SELECT SUM(Num_Violations) FROM SpeedViolations WHERE Violation_Date = ?) AS SpeedViolations;
    """
    dbCursor.execute(sql,(userInput,userInput))
    row = dbCursor.fetchone()
    red = int(row[0]) if row[0] is not None else 0
    speed = int(row[1]) if row[1] is not None else 0
    total = red + speed
    if(total == 0):
        print("No violations on record for that date.")
    else:
        print("Number of Red Light Violations:", f"{red:,}", f"({red/total*100:.3f}%)")
        print("Number of Speed Violations:", f"{speed:,}", f"({speed/total*100:.3f}%)")
        print("Total Number of Violations: ", f"{total:,}")
        
##################################################################  
#
# commandFour
#
# Given a connection to the database, executes two
# SQL queries to retrieve and output the number of cameras at each intersection
#
def commandFour(dbConn):
    dbCursor = dbConn.cursor()
    sqlred = """
    SELECT Intersections.Intersection_ID, Intersections.Intersection, COUNT(RedCameras.Camera_ID) AS RedCameraCount, (SELECT COUNT(*) FROM RedCameras)
    FROM Intersections
    JOIN RedCameras ON Intersections.Intersection_ID = RedCameras.Intersection_ID
    GROUP BY Intersections.Intersection_ID, Intersections.Intersection
    ORDER BY RedCameraCount DESC, Intersections.Intersection_ID DESC;
    """
    sqlspeed = """
    SELECT Intersections.Intersection_ID, Intersections.Intersection, COUNT(SpeedCameras.Camera_ID) AS SpeedCameraCount,  (SELECT COUNT(*) FROM SpeedCameras)
    FROM Intersections
    JOIN SpeedCameras ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
    GROUP BY Intersections.Intersection_ID, Intersections.Intersection
    ORDER BY SpeedCameraCount DESC, Intersections.Intersection_ID DESC;
    """
    dbCursor.execute(sqlred)
    rows = dbCursor.fetchall()
    print("Number of Red Light Cameras at Each Intersection")
    for row in rows:
        print(f"  {row[1]} ({row[0]}) : {row[2]} ({row[2]/row[3]*100:.3f}%)") 
    print()
    dbCursor.execute(sqlspeed)
    rows = dbCursor.fetchall()
    print("Number of Speed Cameras at Each Intersection")
    for row in rows:
        print(f"  {row[1]} ({row[0]}) : {row[2]} ({row[2]/row[3]*100:.3f}%)")

##################################################################  
#
# commandFive
#
# Given a connection to the database and a year in the format: YYYY, executes two
# SQL queries to retrieve and output the number of violations at each intersection
#
def commandFive(dbConn,userInput):
    dbCursor = dbConn.cursor()
    sqlred = """
    SELECT Intersections.Intersection_ID, Intersections.Intersection, SUM(RedViolations.Num_Violations) AS RedViolations, (SELECT SUM(Num_Violations) FROM RedViolations WHERE strftime('%Y', Violation_Date) = ?)
    FROM Intersections 
    JOIN RedCameras ON Intersections.Intersection_ID = RedCameras.Intersection_ID
    JOIN RedViolations ON RedCameras.Camera_ID = RedViolations.Camera_ID
    WHERE strftime('%Y', RedViolations.Violation_Date) = ?
    GROUP BY Intersections.Intersection_ID, Intersections.Intersection
    ORDER BY RedViolations DESC;
    """

    sqlspeed = """
    SELECT Intersections.Intersection_ID, Intersections.Intersection, SUM(SpeedViolations.Num_Violations) AS SpeedViolations, (SELECT SUM(Num_Violations) FROM SpeedViolations WHERE strftime('%Y', Violation_Date) = ?)
    FROM Intersections 
    JOIN SpeedCameras ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
    JOIN SpeedViolations ON SpeedCameras.Camera_ID = SpeedViolations.Camera_ID
    WHERE strftime('%Y', SpeedViolations.Violation_Date) = ?
    GROUP BY Intersections.Intersection_ID, Intersections.Intersection
    ORDER BY SpeedViolations DESC;
    """
    dbCursor.execute(sqlred,(userInput,userInput))
    rows = dbCursor.fetchall()
    total = 0
    print()
    print("Number of Red Light Violations at Each Intersection for", userInput)
    if(len(rows)==0):
        print("No red light violations on record for that year.")
    else:
        for row in rows:
            print(f"  {row[1]} ({row[0]}) : {row[2]:,} ({row[2]/row[3]*100:.3f}%)")
            total = total + row[2]
        print("Total Red Light Violations in",userInput, ":", f"{total:,}")
    print()
    dbCursor.execute(sqlspeed,(userInput,userInput))
    rows = dbCursor.fetchall()
    total = 0
    print("Number of Speed Violations at Each Intersection for",userInput)
    if(len(rows)==0):
        print("No speed violations on record for that year.")
    else:
        for row in rows:
            print(f"  {row[1]} ({row[0]}) : {row[2]:,} ({row[2]/row[3]*100:.3f}%)")
            total = total + row[2]
        print("Total Speed Violations in",userInput, ":",f"{total:,}")
    print()

##################################################################  
#
# commandSix
#
# Given a connection to the database, a camera ID, and a pyplot object, executes two
# SQL queries to retrieve and output the number of violations by year for that camera.
# The user will also have the option to plot that info on a graph
#
def commandSix(dbConn,userInput,plt):
    x=[]
    y=[]
    dbCursor = dbConn.cursor()
    sqlred = """
    SELECT strftime('%Y', Violation_Date) AS Year, SUM(Num_Violations)
    FROM RedViolations
    WHERE Camera_ID = ?
    GROUP BY Year
    ORDER BY Year ASC;
    """
    sqlspeed = """
    SELECT strftime('%Y', Violation_Date) AS Year, SUM(Num_Violations)
    FROM SpeedViolations
    WHERE Camera_ID = ?
    GROUP BY Year
    ORDER BY Year ASC;
    """
    i = 0
    title = "Yearly Violations for Camera " + userInput
    dbCursor.execute(sqlred,(userInput,))
    rows = dbCursor.fetchall()
    if(len(rows)!=0):
        print("Yearly Violations for Camera",userInput)
        for row in rows:
            print(f"{row[0]} : {row[1]:,}")
            x.append(row[0])
            y.append(row[1])
        print()
        newUserInput = input("Plot? (y/n) ")
        if(newUserInput == "y"):
            plt.xlabel("Year")
            plt.ylabel("Number of Violations")
            plt.title(title)
            plt.ioff()
            plt.plot(x,y)
            plt.show()
    else: 
        i=i+1
    dbCursor.execute(sqlspeed,(userInput,))
    rows = dbCursor.fetchall()
    if(len(rows)!=0):
        print("Yearly Violations for Camera",userInput)
        for row in rows:
            print(f"{row[0]} : {row[1]:,}")
            x.append(row[0])
            y.append(row[1])
        print()
        newUserInput = input("Plot? (y/n) ")
        if(newUserInput == "y"):
            plt.xlabel("Year")
            plt.ylabel("Number of Violations")
            plt.title(title)
            plt.ioff()
            plt.plot(x,y)
            plt.show()
    else:
        i=i+1
    if(i==2):
        print("No cameras matching that ID were found in the database.")

##################################################################  
#
# commandSeven
#
# Given a connection to the database, a camera ID, year in the format: YYYY, and a pyplot object, executes an
# SQL querie to retrieve and output the number of violations by month for that camera for that year.
# The user will also have the option to plot that info on a graph
#
def commandSeven(dbConn,userInputA,plt):
    sql = """
    SELECT 'Red' AS CameraType FROM RedCameras WHERE Camera_ID = ?
    UNION
    SELECT 'Speed' AS CameraType FROM SpeedCameras WHERE Camera_ID = ?;
    """
    dbCursor = dbConn.cursor()
    dbCursor.execute(sql,(userInputA,userInputA))
    row = dbCursor.fetchone()
    if (not row):
        print("No cameras matching that ID were found in the database.")
        return
    userInputB = input("Enter a year: ")
    x=[]
    y=[]
    plt.xlabel("Month")
    plt.ylabel("Number of Violations")
    title = "Monthly Violations for Camera " + userInputA + " (" + userInputB + ")"
    plt.title(title)
    sqlred="""
    SELECT strftime('%m', Violation_Date) AS Month, SUM(Num_Violations)
    FROM RedViolations
    WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
    GROUP BY Month
    ORDER BY Month ASC;
    """
    sqlspeed="""
    SELECT strftime('%m', Violation_Date) AS Month, SUM(Num_Violations)
    FROM SpeedViolations
    WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
    GROUP BY Month
    ORDER BY Month ASC;
    """
    dbCursor.execute(sqlred,(userInputA,userInputB))
    rows = dbCursor.fetchall()
    print("Monthly Violations for Camera",userInputA, "in", userInputB)
    for row in rows:
        print(f"{row[0]}/{userInputB} : {row[1]:,}")
        x.append(row[0])
        y.append(row[1])

    dbCursor.execute(sqlspeed,(userInputA,userInputB))
    rows = dbCursor.fetchall()
    for row in rows:
        print(f"{row[0]}/{userInputB} : {row[1]:,}")
        x.append(row[0])
        y.append(row[1])
    print()
    newUserInput = input("Plot? (y/n) ")
    if(newUserInput == "y"):
        plt.ioff
        plt.plot(x,y)
        plt.show()
    
##################################################################  
#
# commandEight
#
# Given a connection to the database, a year in the format: YYYY, and a pyplot object, executes two
# SQL queries to retrieve and output the number of violations for that year and compares them.
# The user will also have the option to plot that info on a graph
#
def commandEight(dbConn,userInput,plt):
    plt.xlabel("Day")
    plt.ylabel("Number of Violations")
    title = "Violations Each Day of " + userInput
    plt.title(title)
    dbCursor = dbConn.cursor()
    sqlred = """
    SELECT Violation_Date, SUM(Num_Violations)
    FROM RedViolations
    WHERE strftime('%Y', Violation_Date) = ?
    GROUP BY Violation_Date
    ORDER BY Violation_Date ASC;
    """
    sqlspeed="""
    SELECT Violation_Date, SUM(Num_Violations)
    FROM SpeedViolations
    WHERE strftime('%Y', Violation_Date) = ?
    GROUP BY Violation_Date
    ORDER BY Violation_Date ASC;
    """
    dbCursor.execute(sqlred,(userInput,))
    redRows = dbCursor.fetchall()
    dbCursor.execute(sqlspeed,(userInput,))
    speedRows = dbCursor.fetchall()

    redDict = dict(redRows)
    speedDict = dict(speedRows)

    startDate = datetime(int(userInput), 1, 1)
    endDate = datetime(int(userInput), 12, 31)
    allDates = [(startDate + timedelta(days=i)).strftime('%Y-%m-%d')
             for i in range((endDate - startDate).days + 1)]
    
    redSeries = [(date, redDict.get(date, 0)) for date in allDates]
    speedSeries = [(date, speedDict.get(date, 0)) for date in allDates]

    print("Red Light Violations:")
    for date, count in redSeries[:5]:
        if(count != 0):
            print(f"{date} {count}")
    for date, count in redSeries[-5:]:
        if(count != 0):
            print(f"{date} {count}")

    print("Speed Violations:")
    for date, count in speedSeries[:5]:
        if(count != 0):
            print(f"{date} {count}")
    for date, count in speedSeries[-5:]:
        if(count != 0):
            print(f"{date} {count}")
    print()
    
    userInput = input("Plot? (y/n) ")
    if(userInput == "y"):
        dates = [datetime.strptime(d, '%Y-%m-%d') for d, _ in redSeries]
        red_counts = [count for _, count in redSeries]
        speed_counts = [count for _, count in speedSeries]

        plt.ioff()
        plt.plot(dates, red_counts, color='red', label='Red Light')
        plt.plot(dates, speed_counts, color='orange', label='Speed')
        plt.legend()
        plt.show()

##################################################################  
#
# commandNine
#
# Given a connection to the database, a street name, and a pyplot object, executes two
# SQL queries to retrieve and output find all the cameras on that street
# The user will also have the option to plot that info on a map of Chicago
#
def commandNine(dbConn,userInput,plt):
    dbCursor = dbConn.cursor()
    sqlred="""
    SELECT Camera_ID, Address, Latitude, Longitude
    FROM RedCameras
    WHERE Address LIKE '%' || ? || '%'
    ORDER BY Camera_ID ASC;
    """
    sqlspeed="""
    SELECT Camera_ID, Address, Latitude, Longitude
    FROM SpeedCameras
    WHERE Address LIKE '%' || ? || '%'
    ORDER BY Camera_ID ASC;
    """
    dbCursor.execute(sqlred,(userInput,))
    redRows = dbCursor.fetchall()
    dbCursor.execute(sqlspeed,(userInput,))
    speedRows = dbCursor.fetchall()

    if not redRows and not speedRows:
        print("There are no cameras located on that street.")
        return
    else:
        print()
        print("List of Cameras Located on Street:", userInput)
        print("  Red Light Cameras:")
        for row in redRows:
            print(f"     {row[0]} : {row[1]} ({row[2]}, {row[3]})")
        print("  Speed Cameras:")
        for row in speedRows:
            print(f"     {row[0]} : {row[1]} ({row[2]}, {row[3]})")

    userInput = input("Plot? (y/n) ")
    if(userInput == "y"):
        image = plt.imread("chicago.png")
        xydims= [-87.9277,-87.5569, 41.7012, 42.0868] 
        plt.imshow(image, extent=xydims)
        title = "Cameras on Street: " + userInput
        plt.title(title)

        xRed = [row[3] for row in redRows]
        yRed = [row[2] for row in redRows]
        xSpeed = [row[3] for row in speedRows]
        ySpeed = [row[2] for row in speedRows]

        plt.plot(xRed,yRed,color="red",marker="o")
        plt.plot(xSpeed,ySpeed,color="orange",marker="o")
        for row in redRows:
            plt.annotate(str(row[0]), (row[3],row[2]))
        for row in speedRows:
            plt.annotate(str(row[0]), (row[3],row[2]))
        plt.xlim([-87.9277,-87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()


##################################################################  
#
# main
#
dbConn = sqlite3.connect('cameras.sqlite')

print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Fall 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()

while True:
    print("Select a menu option: ")
    print("  1. Find an intersection by name")
    print("  2. Find all cameras at an intersection")
    print("  3. Percentage of violations for a specific date")
    print("  4. Number of cameras at each intersection")
    print("  5. Number of violations at each intersection, given a year")
    print("  6. Number of violations by year, given a camera ID")
    print("  7. Number of violations by month, given a camera ID and year")
    print("  8. Compare the number of red light and speed violations, given a year")
    print("  9. Find cameras located on a street")
    print("or x to exit the program.")
    userInput = input("Your choice --> ")
    if(userInput == "x"):
        break
    try:
        result = int(userInput)
        if(result == 1):
            print()
            userInput = input("Enter the name of the intersection to find (wildcards _ and % allowed): ")
            commandOne(dbConn,userInput)
        elif(result == 2):
            print()
            userInput = input("Enter the name of the intersection (no wildcards allowed): ")
            commandTwo(dbConn,userInput)
        elif(result == 3):
            print()
            userInput = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): ")
            commandThree(dbConn,userInput)
        elif(result == 4):
            print()
            commandFour(dbConn)
        elif(result == 5):
            print()
            userInput = input("Enter the year that you would like to analyze: ")
            commandFive(dbConn,userInput)
        elif(result == 6):
            print()
            userInput = input("Enter a camera ID: ")
            commandSix(dbConn,userInput,plt)
        elif(result == 7):
            print()
            userInputA = input("Enter a camera ID: ")
            commandSeven(dbConn,userInputA,plt)
        elif(result == 8):
            print()
            userInput = input("Enter a year: ")
            commandEight(dbConn,userInput,plt) 
        elif(result == 9):
            print()
            userInput = input("Enter a street name: ")
            commandNine(dbConn,userInput,plt)
        else:
            print("Error, unknown command, try again...")
    except ValueError:
        print("Error, unknown command, try again...")
    print()


print("Exiting program.")
#
# done
#
