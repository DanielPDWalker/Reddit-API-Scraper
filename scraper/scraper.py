import praw
import pandas as pd
import numpy as np
#import reddit login details file from config.py file
import config

#Set up a reddit instance. Uses login details from config.py
reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     username=config.username,
                     password=config.password,
                     user_agent=config.user_agent)

#Set the subreddit we will be accessing.
subreddit = reddit.subreddit('spacex')
#Store the wiki page we want to reference.
wiki = subreddit.wiki['/launches/manifest']
#Scrape all the information on stored wiki page.
data = wiki.content_md
#Splits data on markup for heading '##', as these are titles for our tables.
one,futureLaunches,pastLaunches,orbits,notes,six,seven,eight = data.split('##')

#FUNCTIONS

def cleaningFunction(tableName):
    if tableName == 'notes':
        tableName = tableName.split('.')
    else:
        tableName = tableName.split('|')
        
    tableName = [i.replace('\r\n', '|') for i in tableName]
    tableName = [i.replace('\n', ' ') for i in tableName]
    tableName = [i.replace('\r', ' ') for i in tableName]
    tableName = [i.replace('(#red)', ' ') for i in tableName]
    tableName = [i.replace('(#green)', ' ') for i in tableName]
    tableName = [i.rstrip() for i in tableName]
    tableName = [i.lstrip() for i in tableName]
    tableName = [i.strip('|') for i in tableName]
    tableName = [i+'|' for i in tableName]

    tableNameString = ''

    for i in tableName:
        tableNameString = tableNameString+i

    tableName = tableNameString.split('|')

    for i in tableName:
        if i == '':
            tableName.remove(i)


    return tableName


def removeMarkdownLinks(removeLinksList):
    newList = []
    for i in removeLinksList:
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
     



#ORBITS !!!!!! TO CLEAN UP - LIKE pastLaunches!!
orbits = cleaningFunction(orbits)

targetElement1 = 'Orbit Acronym'
targetElement2 = 'Comments'
try:
    targetIndex1 = orbits.index(targetElement1)
    targetIndex2 = orbits.index(targetElement2)+1
except ValueError:
    targetIndex1 = None
    targetIndex2 = None

orbitsHeadings = orbits[targetIndex1:targetIndex2]
orbitsHeading = removeMarkdownLinks(orbitsHeadings)

#Cutting the front title/paragraph off of the orbits table. 
try:
    #The +7 at the end is to remove the empty row before the rest of the table.
    targetIndex = orbits.index(targetElement2)+7
except ValueError:
    targetIndex = None

#Sets the orbits table to the correct starting index.
orbits = orbits[targetIndex:]



#NOTES !!!!!! KEEPING
notes = cleaningFunction(notes)
notesHeadings = []
notesHeadings.append(notes[0])
del notes[0]



#PAST LAUNCHES !!!!!!
pastLaunches = cleaningFunction(pastLaunches)

#The first and last items in the list for the column names. (Used for getting rid of the
#column heads for the data on the rest of the table as well).
targetElement1 = 'Date'
targetElement2 = 'Landing outcome'
try:
    targetIndex1 = pastLaunches.index(targetElement1)
    #You have to +1 the last index as it counts up to but not including it.
    targetIndex2 = pastLaunches.index(targetElement2)+1
except ValueError:
    targetIndex1 = None
    targetIndex2 = None

#Pulls the headings out and saves them for use in creating the dataframe later.
pastLaunchesHeadings = pastLaunches[targetIndex1:targetIndex2]
pastLaunchesHeadings = removeMarkdownLinks(pastLaunchesHeadings)

#Cutting the front title/paragraph off of the pastLaunches table. 
try:
    #The + 11 at the end is to remove the empty row before the rest of the table.
    targetIndex = pastLaunches.index(targetElement2)+11
except ValueError:
    targetIndex = None

#Sets the pastLaunches table to the correct starting index.
pastLaunches = pastLaunches[targetIndex:]



#FUTURE LAUNCHES !!!!!!
futureLaunches = cleaningFunction(futureLaunches)

targetElement1 = 'NET Date [Launch window UTC]'
targetElement2 = '[Notes](https://www.reddit.com/r/spacex/wiki/launches/manifest#wiki_notes) & [Refs](https://www.reddit.com/r/spacex/wiki/launches/manifest#wiki_sources)  '
try:
    targetIndex1 = futureLaunches.index(targetElement1)
    targetIndex2 = futureLaunches.index(targetElement2)+1
except ValueError:
    targetIndex1 = None
    targetIndex2 = None

futureLaunchesHeadings = futureLaunches[targetIndex1:targetIndex2]
futureLaunchesHeadings[7] = 'Notes & Refs'
futureLaunchesHeadings = removeMarkdownLinks(futureLaunchesHeadings)

try:
    targetIndex = futureLaunches.index(targetElement2)+9
except ValueError:
    targetIndex = None

futureLaunches = futureLaunches[targetIndex:]

#DATAFRAMES !!!!!! - TO SORT AFTER ABOVE!!

orbitsDF = pd.DataFrame(np.array(orbits).reshape(-1,6), columns = orbitsHeadings)
notesDF = pd.DataFrame(np.array(notes).reshape(-1,1), columns = notesHeadings)
pastLaunchesDF = pd.DataFrame(np.array(pastLaunches).reshape(-1,10), columns = pastLaunchesHeadings)
futureLaunchesDF = pd.DataFrame(np.array(futureLaunches).reshape(-1, 8), columns = futureLaunchesHeadings)



#SAVE TO CSV

orbitsDF.to_csv('orbits.csv',index_label='index')
notesDF.to_csv('notes.csv',index_label='index')
pastLaunchesDF.to_csv('pastlaunches.csv',index_label='index')
futureLaunchesDF.to_csv('futureLaunches.csv',index_label='index')
