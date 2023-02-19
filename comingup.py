import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import *
from datetime import datetime
import time
from telegram import *

def todaysgames():
    current_time = datetime.now()
    now = current_time.strftime("%Y-%m-%d")

    querystring = "SELECT * FROM FIXTURES where ko_time like '%s%%'" % (now)

    engine = create_engine(sqlprem)

    tg = []

    df = pd.read_sql(text(querystring), con=engine)

    if df.empty:
        print("No games today!")
        exit()
        
    else:
        for index, row in df.iterrows():
            homeTeam = str(row['home'])
            awayTeam = str(row['away'])
            koTime = str(row['ko_time'])[11:-3]
            fixID = str(row['fix_id'])
            game = '%s v %s at %s' %(homeTeam,awayTeam,koTime)
            tg.append(game)

    sendmes('⚽ Today\'s Games ⚽')

    for x in tg:
        print(x)
        sendmes(x)

todaysgames()
