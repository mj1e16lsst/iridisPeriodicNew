#Strat = ['astro152','astro169','astro630','astro1304','astro1322']
#Strat = ['astro152','astro169','astro630','astro1304','astro1322','minion152','minion169','minion630','minion1304','minion1322','minionOC152','minionOC169','minionOC630','minionOC1304','minionOC1322','panstars152','panstars169','panstars630','panstars1304','panstars1322']
name = ['astro','minion','minionOC','panstars','baseline']
number = ['1304','1322','630','169','1929','3311']

for x,na in enumerate(name):
    for y,num in enumerate(number):
	strat = na+num  
        f = open(strat+'.py','r')
        data = f.read()
        f.close()
        loc1 = data.find('startnumber = 0')
        loc2 = loc1 + 16
        f1 = open('noVMastro152.sh','r')
        data1 = f1.read()
        f1.close()
        loc3 = data1.find('astro152.')
        #print(data[loc1:loc1+8])
        loc4 = data1.find('.py')
        print(data1[loc3:loc3+8])
        for x in range(0,20):
            f2 = open(strat+'_'+str(x)+'.py','w')
            f2.write(data[:loc2]+'+ '+str(x)+data[loc2:])
            f2.close()
            f3 = open('noVM'+strat+'_'+str(x)+'.sh','w')
            f3.write(data1[:loc3]+strat+'_'+str(x)+data1[loc4:])
            f3.close()
	    f4 = open('noVM'+strat+'_'+str(x)+'.sh','r')
	    data4 = f4.read()
	    noVMer = '#PBS -N noVM'
            loc5 = data4.find(noVMer)+len(noVMer)
	    f5 = open('noVM'+strat+'_'+str(x)+'.sh','w')
	    f5.write(data4[:loc5]+'_'+strat+'_'+str(x)+data4[loc5:])

