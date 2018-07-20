import subprocess

names = ['minion','panstars']
numbers = ['152','169','630','1304','1322']

for i,name in enumerate(names):
    for n,num in enumerate(numbers):
        subprocess.call(['cp','astro'+num+'.py',name+num+'.py'])
