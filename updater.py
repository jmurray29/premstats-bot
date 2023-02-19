import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.types import *
import requests
import time
import warnings
from telegram import *
warnings.simplefilter(action='ignore', category=FutureWarning)
import os
sqlprem = os.environ.get('sqlprem')
apitoken = os.environ.get('apitoken')
engine = create_engine(sqlprem)

def requestcounter():
    with open('requestcount.txt', 'r') as f:
        output = int(f.read())

    output += 1

    if output > 100:
        sendmes('%s'%(output))

    with open('requestcount.txt', 'w') as f:
        f.write(str(output))

def updateFix():
    now = datetime.now()
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    querystring = {"league":"39","season":"2022"}

    headers = {
            "X-RapidAPI-Key": apitoken,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

    resp = requests.request("GET", url, headers=headers, params=querystring)
    requestcounter()

    data = resp.json()

    fix_list = []
    col_list = ['home','home_id','away','away_id','ko_time','venue','fix_id','ref','fh_time','sh_time','status','elapsed','rnd','home_goals','away_goals','home_win','away_win','ht_home_goals','ht_away_goals','ft_home_goals','ft_away_goals']

    def epochange(time):
        if isinstance(time, int) == True:
            dt = datetime.fromtimestamp(time)
            return(dt)
        else:
            dt = ''
            return(dt)

    for x in data['response']:
        home = x['teams']['home']['name']
        home_id = x['teams']['home']['id']
        away = x['teams']['away']['name']
        away_id = x['teams']['away']['id']
        ko_time = datetime.fromtimestamp(x['fixture']['timestamp'])
        venue = x['fixture']['venue']['name']
        fix_id = x['fixture']['id']
        ref = x['fixture']['referee']
        fh_time = epochange(x['fixture']['periods']['first'])
        sh_time = epochange(x['fixture']['periods']['second'])
        status = x['fixture']['status']['short']
        elapsed = x['fixture']['status']['elapsed']
        rnd = x['league']['round']
        home_goals = x['goals']['home']
        away_goals = x['goals']['away']
        home_win = x['teams']['home']['winner']
        away_win = x['teams']['away']['winner']
        ht_home_goals = x['score']['halftime']['home']
        ht_away_goals = x['score']['halftime']['away']
        ft_home_goals = x['score']['fulltime']['home']
        ft_away_goals = x['score']['fulltime']['away']
        new_list = [home,home_id,away,away_id,ko_time,venue,fix_id,ref,fh_time,sh_time,status,elapsed,rnd,home_goals,away_goals,home_win,away_win,ht_home_goals,ht_away_goals,ft_home_goals,ft_away_goals]
        fix_list.append(new_list)

    updated = now.strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame(columns=col_list, data=fix_list)
    engine.execute("TRUNCATE TABLE FIXTURES")
    df.to_sql('FIXTURES', con=engine, if_exists='append', index=False)
    #print('SUCCESS! ',updated,' ', request)

def updateStats(fix_id):

    try:
        now = datetime.now()

        engine = create_engine(sqlprem)

        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"

        querystring = {"fixture":fix_id}

        headers = {
            "X-RapidAPI-Key": "813ab829bbmsh2264f4492872ca4p153c5ajsndcb3fff07537",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        resp = requests.request("GET", url, headers=headers, params=querystring)
        requestcounter()

        data = resp.json()

        all_stats = []
        col_list = ['team','team_id','home','fix_id','shots_on_goal','shots_off_goals','total_shots','blocked_shots','shots_insidebox','shots_outsidebox','fouls','corner_kicks','offsides','ball_posession','yellow_cards','red_cards','goalkeeper_saves','total_passes','passes_accuracy','passes_percentage','updated']



        fixture_id = data['parameters']['fixture']

        for i in range(0,2):
            #print(i)
            stats = data['response'][i]['statistics']
            team = data['response'][i]['team']['name']
            team_id = data['response'][i]['team']['id']

            if i == 0:
                home = True
            else:
                home = False

            shots_on_goal = stats[0]['value']
            shots_off_goals = stats[1]['value']
            total_shots = stats[2]['value']
            blocked_shots = stats[3]['value']
            shots_insidebox = stats[4]['value']
            shots_outsidebox = stats[5]['value']
            fouls = stats[6]['value']
            corner_kicks = stats[7]['value']
            offsides = stats[8]['value']
            ball_posession = str(stats[9]['value']).replace('%','')
            yellow_cards = stats[10]['value']
            red_cards = stats[11]['value']
            goalkeeper_saves = stats[12]['value']
            total_passes = stats[13]['value']
            passes_accuracy = stats[14]['value']
            passes_percentage = str(stats[9]['value']).replace('%','')

            updated = now.strftime("%Y-%m-%d %H:%M:%S")
            
            engine.execute("DELETE FROM `FIXSTATS` WHERE `fix_id` = '%s' AND `home` = %s" %(fix_id,home))

            all_stats = [team,team_id,home,fixture_id,shots_on_goal,shots_off_goals,total_shots,blocked_shots,shots_insidebox,shots_outsidebox,fouls,corner_kicks,offsides,ball_posession,yellow_cards,red_cards,goalkeeper_saves,total_passes,passes_accuracy,passes_percentage,updated]
            df = pd.DataFrame([all_stats],columns=col_list)
            df.to_sql('FIXSTATS', con=engine, if_exists='append', index=False)
            #print('SUCCESS! ',updated,' ',fix_id)

    except IndexError:
        print('No data for %s yet'%(fix_id))

def todaysGames(): #returns ids of games today
    current_time = datetime.now()
    now = current_time.strftime("%Y-%m-%d")

    querystring = "SELECT * FROM FIXTURES where ko_time like '%s%%'" % (now)

    tg = []

    df = pd.read_sql(text(querystring), con=engine)

    if df.empty:
        return tg
   
    else:
        for index, row in df.iterrows():
            fixID = str(row['fix_id'])
            tg.append(fixID)
        return tg

def liveGames():
    querystring = "SELECT * FROM `FIXTURES` WHERE NOT `status` = 'FT' AND NOT `status` = 'NS' AND NOT `status` = 'PST' AND NOT `status` = 'CANC' AND NOT `status` = 'ABD'"
    df = pd.read_sql(text(querystring), con=engine)

    lg = []

    if df.empty:
        return lg

    else:
        for index, row in df.iterrows():
            fixID = str(row['fix_id'])
            lg.append(fixID)
        return lg