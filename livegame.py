import json
import pandas as pd
from datetime import datetime,timedelta
from sqlalchemy import create_engine, text
from sqlalchemy import delete, MetaData
from sqlalchemy.types import *
import requests
import time
from updater import *
from telegram import *

id = '868184'

sendmes('%s'%(id))

def updateTime():
    global nowUNIX
    presentDate = datetime.now()
    nowUNIX = int(datetime.timestamp(presentDate))

fixturestring = "SELECT * FROM FIXTURES WHERE fix_id = %s " % (id)
statsstring = "SELECT * FROM FIXSTATS WHERE fix_id = %s " % (id)

engine = create_engine(sqlprem)

fixdf = pd.read_sql(text(fixturestring), con=engine)
statsdf = pd.read_sql(text(statsstring), con=engine)

homeTeam = fixdf.loc[0,'home']
awayTeam = fixdf.loc[0,'away']

koTime = fixdf.loc[0,'ko_time']
presentDate = datetime.now()

nowUNIX = int(datetime.timestamp(presentDate))
koUNIX = int(datetime.timestamp(koTime))

finalUpdate = False
updateHT = False
updateKO = False

homeScoreOld = 0
awayScoreOld = 0

while True:
    fixdf = pd.read_sql(text(fixturestring), con=engine)
    statsdf = pd.read_sql(text(statsstring), con=engine)
    gameStatus = fixdf.loc[0,'status']
    updateTime()
    
    homeScore = fixdf.loc[0,'home_goals']
    awayScore = fixdf.loc[0,'away_goals'] 

    if koUNIX > nowUNIX:
        cd = koUNIX - nowUNIX
        print('Game starts in: ',str(timedelta(seconds=cd)))
        time.sleep(10)

    elif gameStatus == 'FT':
        print('Game is OVER!')
        print('%s %s - %s %s'%(homeTeam,homeScore,awayTeam,awayScore))
        sendmes('Game is OVER!')
        sendmes('Final score is: %s %s - %s %s'%(homeTeam,homeScore,awayTeam,awayScore))
        exit()

    elif gameStatus == 'HT':
        if updateHT == False:
            print('%s and %s Half-Time' %(homeTeam,awayTeam))
            sendmes('%s and %s Half-Time' %(homeTeam,awayTeam))
            updateHT = True
            time.sleep(60)
        else:
            time.sleep(10)       

    elif gameStatus == '1H' and updateKO == False:
        print('%s and %s KICK OFF!' %(homeTeam,awayTeam))
        sendmes('%s and %s KICK OFF!' %(homeTeam,awayTeam))      
        updateKO = True

    else:
        print('updated')

        if homeScore != homeScoreOld or awayScore != awayScoreOld :
            if homeScore > 0 or awayScore > 0:
                print('GOAL!! %s %s - %s %s'%(homeTeam,homeScore,awayTeam,awayScore))
                sendmes('GOAL!! %s %s - %s %s'%(homeTeam,homeScore,awayTeam,awayScore))

        homeScoreOld = homeScore
        awayScoreOld = awayScore
        time.sleep(10)
