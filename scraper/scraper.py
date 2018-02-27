# imports
import praw
import pandas as pd
import numpy as np
from datetime import datetime
import re # Add regex to check that first item in list is a date.
          # (Check the data for the table starts at the correct point).
          
# import reddit login details file from config.py file
import config

# Location of the error log file. (Possibly put it in dropbox).
logLocation = 'log.txt'

# Very basic regex to check if the first item in a launch's table's list is a date. (Year specifically).
datePattern = re.compile('^[\d+ ]')

# Regex to check if the first item in the orbit's table's list is at least 2 capital
# letters.
orbitPattern = re.compile('\w*[A-Z]\w*[A-Z]\w*')

# List used to hold items during loops.
holdingList = []

#FUNCTIONS

# This function splits the string of data into a list of clean data.
# No spaces& | & \n or \r or both at the beginning or end.
def cleaningFunction(tableName):

    try:
        # If table is notes then you have to split on the '.' for everything else its the '|'
        if tableName == 'notes':
            tableName = tableName.split('.')
        else:
            tableName = tableName.split('|')
    except:
        # If there is an exception: log the error with the table name.
        errorLog("Error2 - Splitting table's orginal string into list in cleaningFunction. Input table = "+tableName)

    try:
        # Replace with '|' as '\r\n' ALWAYS replaces a ' ' and conncets 2 items in the table. We use the '|' for splitting later.
        tableName = [i.replace('\r\n', '|') for i in tableName]
        # Replace unwanted markup with empty spaces for removal later.
        tableName = [i.replace('\n', ' ') for i in tableName]
        tableName = [i.replace('\r', ' ') for i in tableName]
        tableName = [i.replace('(#red)', ' ') for i in tableName]
        tableName = [i.replace('(#green)', ' ') for i in tableName]
        # Strip the empty spaces before and after each item.
        tableName = [i.rstrip() for i in tableName]
        tableName = [i.lstrip() for i in tableName]
        # Strip and '|' at the front or back of any item in the list. (We add these on in the next step, dont want doubles)
        tableName = [i.strip('|') for i in tableName]
        # Add a | to the end of each item in tableName. (For splitting on)
        tableName = [i+'|' for i in tableName]
    except:
        # If there is an exception: log the error with the table name.
        errorLog('Error3 - List comprehension in cleaningFunction. Input table = '+tableName)

    # Make new string for concatenating the whole list back into a string for a cleaner split.
    tableNameString = ''
    # Concatenate the list into the above string.
    for i in tableName:
        tableNameString = tableNameString+i
    # Split the string, this time cleanly.
    tableName = tableNameString.split('|')
    # Remove any empty items in the list.
    for i in tableName:
        if i == '':
            tableName.remove(i)

    # Return cleaned list.
    return tableName

# This function will remove 1 (one) markup link, and return whatver was in the click-
# able part. "[THIS STUFF IN HERE](www.website.com)" and not the [] or actual webaddress.
# It only checks for the first [ untill the first ] so only the first link in each
# item will be returned.
def removeOneMarkdownLink(removeOneLinkList):
    newList = []
    for i in removeOneLinkList:
        if i[0] == '[':
            targetElement = ']'
            splitWord = list(i)
            for l in splitWord:
                if l == ']':
                    targetIndex = splitWord.index(l)
                    newList.append(i[1:targetIndex])
        else:
            newList.append(i)
    return newList

# !!!!!!!!!!!!! MAKE FUNCTION TO REMOVE MULTIPLE MARKDOWN LINKS !!!!!!!!!!!!!




# This is the error logging function. You just pass in the message to be logged.
def errorLog(errorMessage):
    # The logLocation is set at the top of the script. (Incase you change it later).
    # We use 'w' so we just overwrite any previous errors logged, no need to keep a log
    # once they are fixed.
    log = open(logLocation,'w')
    # datetime.now().ctime() is date and time to seconds of when this error was produced/
    # when the script was run.
    log.write('Error at date + time: '+datetime.now().ctime()+'\n')
    log.write(errorMessage)
    log.close()
    # After logging the error exit the script. (We dont want unuseable csv files being
    # produced after encountering an error).
    sys.exit()

# Regex function to make sure the first item in a launch's table's list is a date.
# Currently checks that the first thing in the string is a number of digits followed by a space.
def setFirstItemToDate(tableName):
    for i in tableName:
        # Save the match return (matched object returned or none).
        m = re.match(datePattern,i)
        # If m != None
        if m:
            # Save to a new list the tables data sliced at the index of the match (i)
            # though to the end of the list.
            holdingList = tableName[tableName.index(i):]
            # Once your found and saved your first match, break out of all if and fors.
            break
    # Return the newly sliced list, that will have your tables first item as its first item.
    return holdingList


# Using the orbit regex pattern of 2 capital letter in a row or more. (Checking against
# a acronym column.

# For comments see : setFirstItemToDate
def orbitRegex(tableName):
    for i in tableName:
        m = re.match(orbitPattern,i)
        if m:
            holdingList = tableName[tableName.index(i):]
            break
    return holdingList



# Set up a reddit instance. Uses login details from config.py
reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     username=config.username,
                     password=config.password,
                     user_agent=config.user_agent)

# Set the subreddit we will be accessing.
subreddit = reddit.subreddit('spacex')
# Store the wiki page we want to reference.
wiki = subreddit.wiki['/launches/manifest']
# Scrape all the information on stored wiki page.
data = wiki.content_md



# Splits data on markup for heading '##', as these are titles for our tables.
try:
    one,futureLaunches,pastLaunches,orbits,notes,six,seven,eight = data.split('##')
except:
    # If there is an exception: log the error.
    errorLog('Error1 - Splitting the imported data at the ## markup headings')





#PAST LAUNCHES
# Pass the current string pastLaunches to the cleaningFunction to have a cleaned list
# returned and saved in its place.
pastLaunches = cleaningFunction(pastLaunches)

# The first and last items in the list for the column names. (Used for getting rid of the
# column heads for the data on the rest of the table as well).
targetElement1 = 'Date'
targetElement2 = 'Landing outcome'
try:
    targetIndex1 = pastLaunches.index(targetElement1)
    # You have to +1 the last index as it counts up to but not including it.
    targetIndex2 = pastLaunches.index(targetElement2)+1
except:
    errorLog('Error 4 - Getting the indexes for slicing the pastLaunches list to make the pastLaunchesHeadings list. Likely targetElemets have changed.') 

# Pulls the headings out and saves them for use in creating the dataframe later.
pastLaunchesHeadings = pastLaunches[targetIndex1:targetIndex2]
pastLaunchesHeadings = removeOneMarkdownLink(pastLaunchesHeadings)

# Uses setFirstItemToDate to make sure the starting item of the list is a date.
# (The first column on the launches tables are dates).
pastLaunches = setFirstItemToDate(pastLaunches)




#FUTURE LAUNCHES
# For comments see the pastLaunches section.
futureLaunches = cleaningFunction(futureLaunches)

targetElement1 = 'NET Date [Launch window UTC]'
targetElement2 = '[Notes](https://www.reddit.com/r/spacex/wiki/launches/manifest#wiki_notes) & [Refs](https://www.reddit.com/r/spacex/wiki/launches/manifest#wiki_sources)  '
try:
    targetIndex1 = futureLaunches.index(targetElement1)
    targetIndex2 = futureLaunches.index(targetElement2)+1
except:
    errorLog('Error 6 - Getting the indexes for slicing the futureLaunches list to make the futureLaunchesHeadings list. Likely targetElemets have changed.') 

futureLaunchesHeadings = futureLaunches[targetIndex1:targetIndex2]
futureLaunchesHeadings[futureLaunchesHeadings.index(targetElement2)] = 'Notes & Refs'
futureLaunchesHeadings = removeOneMarkdownLink(futureLaunchesHeadings)

futureLaunches = setFirstItemToDate(futureLaunches)




#ORBITS
# For comments see the pastLaunches section.
orbits = cleaningFunction(orbits)

targetElement1 = 'Orbit Acronym'
targetElement2 = 'Comments'
try:
    targetIndex1 = orbits.index(targetElement1)
    targetIndex2 = orbits.index(targetElement2)+1
except:
    errorLog('Error 5 - Getting the indexes for slicing the orbits list to make the orbitsHeadings list. Likely targetElemets have changed.') 

orbitsHeadings = orbits[targetIndex1:targetIndex2]
orbitsHeading = removeOneMarkdownLink(orbitsHeadings)

# Uses orbitRegex to make sure the starting item of the list is at least 2 capital letters.
# (The first column on the orbits tables are orbit acronym).
orbits = orbitRegex(orbits)




#NOTES
notes = cleaningFunction(notes)
# Make a new list for the notesHeadings
notesHeadings = []
# Add the first item in the notes list to the notesHeadings list. (This is the table
# name that gets added to notes on the initial markdown split on '##')
notesHeadings.append(notes[0])
# Delete the first item in the notes list, (which is the table name that we dont need).
del notes[0]





#DATAFRAMES !!!!!! - TO SORT AFTER ABOVE!!

# Turns the python list into a numpy array. Then reshapes(rows,columns) into a dataframe,
# where columns = that tables headings. reshape(-1,x) -1 means as many rows as needed.
orbitsDF = pd.DataFrame(np.array(orbits).reshape(-1,6), columns = orbitsHeadings)
notesDF = pd.DataFrame(np.array(notes).reshape(-1,1), columns = notesHeadings)
pastLaunchesDF = pd.DataFrame(np.array(pastLaunches).reshape(-1,10), columns = pastLaunchesHeadings)
futureLaunchesDF = pd.DataFrame(np.array(futureLaunches).reshape(-1, 8), columns = futureLaunchesHeadings)



#SAVE TO CSV

# Create a datetime for the current time, for use in timestamping the csv files.
now = datetime.now()

# We format our date with now.strftime('FORMAT HERE') and concatenate them to the
# filename. Set the index for cleaner importing of the csv file. (Personal preference, could remove).
orbitsDF.to_csv('orbits '+str(now.strftime('%d-%m-%Y'))+'.csv',index_label='index')
notesDF.to_csv('notes '+str(now.strftime('%d-%m-%Y'))+'.csv',index_label='index')
pastLaunchesDF.to_csv('pastlaunches '+str(now.strftime('%d-%m-%Y'))+'.csv',index_label='index')
futureLaunchesDF.to_csv('futureLaunches '+str(now.strftime('%d-%m-%Y'))+'.csv',index_label='index')
