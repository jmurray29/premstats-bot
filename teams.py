import json
import pandas as pd 
import requests
from sqlalchemy import create_engine
from sqlalchemy.types import *
import datetime

engine = create_engine(sqlprem)

teams=['42','50','34','47','33','40','51','49','36','55','52','66','46','35','63','48','45','65','41','39']
code_dict= {
'Arsenal': 'ARS',
'Manchester City': 'MCI',
'Newcastle': 'NEW',
'Tottenham': 'TOT',
'Manchester United': 'MUN',
'Liverpool': 'LIV',
'Brighton': 'BRI',
'Chelsea': 'CHE',
'Fulham': 'FUL',
'Brentford': 'BRE',
'Crystal Palace': 'CRY',
'Aston Villa': 'AVL',
'Leicester': 'LEI',
'Bournemouth': 'BOU',
'Leeds': 'LEE',
'West Ham': 'WHU',
'Everton': 'EVE',
'Nottingham Forest': 'NFO',
'Southampton': 'SOU',
'Wolves' :'WOL'
}

url = "https://api-football-v1.p.rapidapi.com/v3/standings"
url2 = "https://api-football-v1.p.rapidapi.com/v3/standings"

querystring = {"season":"2022","league":"39"}
querystring2 = {"season":"2022","league":"39"}

headers = {
	"X-RapidAPI-Key": apitoken,
	"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

datalist = []
collist = ['id','rank','name','shrtname','logo','played','win','lose','draw','gf','ga','gd','points','form']

standings = requests.request("GET", url, headers=headers, params=querystring)
sjson = standings.json()
teams = requests.request("GET", url, headers=headers, params=querystring)
tjson = teams.json()

for i in sjson['response'][0]['league']['standings'][0]:
    id = i['team']['id']
    name = i['team']['name']
    shrtname = code_dict[name]
    logo = i['team']['logo']
    played = i['all']['played'] 
    win = i['all']['win'] 
    lose = i['all']['lose']
    draw = i['all']['draw']
    gf = i['all']['goals']['for']
    ga = i['all']['goals']['against']
    gd = i['goalsDiff']
    points = i['points']
    rank = i['rank']
    form = i['form']

    newlist=[id,rank,name,shrtname,logo,played,win,lose,draw,gf,ga,gd,points,form]
    datalist.append(newlist)

df = pd.DataFrame(columns=collist, data=datalist)

engine.execute("TRUNCATE TABLE TEAMS")
df.to_sql('TEAMS', con=engine, if_exists='append', index=False)
print('SUCCESS!')

print(df)
