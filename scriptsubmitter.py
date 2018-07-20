import subprocess

#'astro152','astro169','astro630','astro1304','astro1322'
#Strat = ['minion152','minion169','minion630','minion1304','minion1322','minionOC152','minionOC169','minionOC630','minionOC1304','minionOC1322']#,'panstars152','panstars169','panstars630','panstars1304','panstars1322']
#Strat = ['panstars1304','panstars1322']
#name = ['astro','panstars','minion','minionOC','baseline']
name = ['baseline']
number = ['169','1304','1322','1929','3311','630']
Strat = []
#Strat = ['astro169','minion169','minionOC169','panstars1304','astro3311']
for i,na in enumerate(name):
    for x,nu in enumerate(number):
	Strat.append(na+nu)
#print(Strat)
for y in range(len(Strat)):
    for x in range(0,20):
        subprocess.call(['chmod','+x','/home/mj1e16/periodic/noVM'+Strat[y]+'_'+str(x)+'.sh'])
        subprocess.call(['/local/software/torque/default/bin/qsub','/home/mj1e16/periodic/noVM'+Strat[y]+'_'+str(x)+'.sh'])


