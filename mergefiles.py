import subprocess

name = ['minion','minionOC','astro','panstars']
number = ['152','1304','1322','630','169']

#f = open('testPaste.txt','w+')
#a = open('testPaste.txt','a+')
List = ['paste','-d',' ']
for na in range(len(name)):
    for nu in range(len(number)):
        f = open('combined/combined'+name[na]+number[nu]+'.txt','w+')
        List = ['paste','-d',' ']        
        for x in range(20):
	    List.append('out'+str(name[na])+str(number[nu])+str(x)+'.txt')
           # if name[na]+number[nu] != 'astro1322':
           #     if name[na]+number[nu] != 'panstars1304':
           #         List.append('out'+str(name[na])+str(number[nu])+str(x)+'.txt')
        
	subprocess.call(List,stdout=f)
        #if name[na]+number[nu] != 'astro1322':
        #    if name[na]+number[nu] != 'panstars1304':
        #        subprocess.call(List,stdout=f)

#if x == 0:
    #    subprocess.call(['paste','-d','" "','out'+str(name[0])+str(number[0])+str(x)+'.txt'],stdout=f)
    #else:
    #    subprocess.call(['paste','-d','" "','out'+str(name[0])+str(number[0])+str(x)+'.txt'],stdout=a)
        #print(List)
        #print(name[na],number[nu])        
        #subprocess.call(List,stdout=f)
