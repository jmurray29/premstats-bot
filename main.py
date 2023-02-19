from updater import *

while True:
    updateFix()
    lg = liveGames()

    if lg == []:
        print('no updates')

    for x in lg:
        updateStats(x)
        print('%s updated' %(x))

    time.sleep(60)