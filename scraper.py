import praw
import pandas as pd
import numpy as np
#import reddit login details file from config.py file
import config

reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     username=config.username,
                     password=config.password,
                     user_agent=config.user_agent)

subreddit = reddit.subreddit('spacex')

wiki = subreddit.wiki['/launches/manifest']

data = wiki.content_md

one,upcomingLaunches,pastLaunches,orbits,notes,six,seven,eight = data.split('##')

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



#ORBITS !!!!!! TO CLEAN UP - LIKE pastLaunches!!

'''
orbitsHeadings = orbits[100:206]
orbits = orbits[250:]
orbits = cleaningFunction(orbits)
orbitsHeadings = cleaningFunction(orbitsHeadings)
'''

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


#Cutting the front title/paragraph off of the pastLaunches table. 
try:
    #The + 11 at the end is to remove the empty row before the rest of the table.
    targetIndex = pastLaunches.index(targetElement2)+11
except ValueError:
    targetIndex = None

#Sets the pastLaunches table to the correct starting index.
pastLaunches = pastLaunches[targetIndex:]



#UPCOMING LAUNCHES !!!!!!


#DATAFRAMES !!!!!! - TO SORT AFTER ABOVE!!

#FUTURELAUNCH DF
#orbitsDF = pd.DataFrame(np.array(orbits).reshape(-1,6), columns = orbitsHeadings)
#notesDF = pd.DataFrame(np.array(notes).reshape(-1,1), columns = notesHeadings)

pastLaunchesDF = pd.DataFrame(np.array(pastLaunches).reshape(-1,10), columns = pastLaunchesHeadings)

pastLaunchesDF.to_csv('pastlaunches.csv')
