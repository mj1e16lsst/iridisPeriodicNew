import subprocess

Strategy = ['astro','panstars','minion','minionOC','baseline']
field = ['1304','1322','630','169','1929','3311']

magID = 'newlist = Magnitudes.'
obsID = 'obs = Observations.'
outID = '/home/mj1e16/periodic/out'

for na,name in enumerate(Strategy):
    for nu,number in enumerate(field):
	subprocess.call(['cp','masterFile.py',name+number+'.py'])
	f = open(name+number+'.py','r')
	string = f.read()
	loc1 = string.find(magID) + len(magID)
	#loc2 = string.find(obsID) + len(obsID)
	newstring = string[:loc1]+'mag'+number+string[loc1:]
	loc2 = newstring.find(obsID) + len(obsID)
	if name == 'minionOC':
	    finalstring = newstring[:loc2]+'obs'+name+number+'\nfor y in range(len(obs)):\n    for x in range(len(obs[y])):\n        obs[y][x] = obs[y][x] + ((random.random()*2.)-1.) '+newstring[loc2:]
	else:
	    finalstring = newstring[:loc2]+'obs'+name+number+newstring[loc2:]
	f.close()
	loc3 = finalstring.find(outID) + len(outID)
	newfinalstring = finalstring[:loc3]+name+number+finalstring[loc3:]
	f2 = open(name+number+'.py','w')
	f2.write(newfinalstring)
	f.close()
