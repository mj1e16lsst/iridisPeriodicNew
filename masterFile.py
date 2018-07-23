import lomb_scargle_multiband as periodic
import numpy as np
import os
import random
import Observations
import Magnitudes
import simulate_lc as lc_sim


zeroPoints = [0,26.5,28.3,28.13,27.79,27.4,26.58]
FWHMeff = [0.8,0.92,0.87,0.83,0.80,0.78,0.76] # arcmins?
pixelScale = 0.2
readOut = 12.7
sigSys = 0.005
flareperiod = 4096
flarecycles = 10
dayinsec=86400
background = 40

lim = [0, 23.5, 24.8, 24.4, 23.9, 23.3, 22.1] # limiting magnitude ugry
sat = [0, 14.7, 15.7, 15.8, 15.8, 15.3, 13.9] # sat mag as above

looooops = 1#10000
maglength = 2#20
freqlength = 2#20
processors = 2#20

startnumber = 0                   
endnumber = startnumber + 1

secondstartnumber = 0
secondendnumber = secondstartnumber + 1


inFile = '/home/mj1e16/periodic/out'+str(startnumber)+'_'+str(secondstartnumber)+'.txt'
outFile = '/home/mj1e16/periodic/out'+'_mag_'+str(startnumber)+'_period_'+str(secondstartnumber)+'.txt'
miscFile = '/home/mj1e16/periodic/misc'+'_mag_'+str(startnumber)+'_period_'+str(secondstartnumber)+'.txt'



#obs = Observations.
obs = Observations.obsastro630


def magUncertainy(Filter, objectmag, exposuretime,background, FWHM): # b is background counts per pixel   
    countsPS = 10**((Filter-objectmag)/2.5)
    counts = countsPS * exposuretime
    uncertainty = 1/(counts/((counts/2.3)+(((background/2.3)+(12.7**2))*2.266*((FWHM/0.2)**2)))**0.5) # gain assumed to be 1
    return uncertainty



def averageFlux(observations, Frequency, exptime):
    #b = [0]*len(observations)
    b = np.zeros(len(observations))
    for seconds in range(0, exptime):
        a = np.sin((2*np.pi*(Frequency))*(observations+(seconds/(3600*24))))
        for x in range(len(aOld)):
            if aOld[x] != a[x]:
                print('no in average flux')
        b = a+b
    c = b/exptime
    return c

def Flux(observations,Frequency,exptime):
    a = np.sin((2*np.pi*(Frequency)*observations))
    return a


def ellipsoidalFlux(observations, Frequency,exptime):
    period = 1/(Frequency)
    phase = (observations % (2*period))
    b = np.zeros(len(observations))
    for seconds in range(0, exptime):
        a = np.sin((2*np.pi*(Frequency))*(observations+(seconds/(3600*24))))
        b = a + b
    c = b/exptime
    for x in range(0,len(phase)):
        if (phase[x]+(1.5*period)) < (3*period):
            c[x] = c[x]*(1./3.)
        else:
            c[x] = c[x]*(2./3.)
    return c


longflare = lc_sim.lc_sim(2880*366*11,30,0.,'unbroken',[1.0, 8., 1.0, -1.])
longflare = np.abs(longflare)
STD = np.std(longflare)
longflare = 0.1*(longflare/STD)
longflare.tolist()


f = open(miscFile,'w')
f.write('longflare = '+str(longflare))
f.close()

longflare = np.asarray(longflare)

def lombScargle(frequencyRange,longflare=longflare,objectmag=20,loopNo=looooops,numsteps=10000): # frequency range and object mag in list
       
    results = {}
    totperiod,totmperiod,totpower,SigLevel = [],[],[],[]
    filterletter = ['o','u','g','r','i','z','y']
    
    period = 1/(frequencyRange) 
    
    fmin=(1/30)  
    fmax=(1/0.003) 
    
    df = (fmax-fmin)/numsteps
    modulationAmplitude=0.1
    
    measuredpower = [] # reset

    y = [[], [], [], [], [], [], []]
    for z in range(1, len(y)):
        y[z] = modulationAmplitude*(ellipsoidalFlux(obs[z], frequencyRange,30))
        for G in range(0, len(y[z])):
            flareMinute = int(round(((obs[z][G]-obs[0][0])*24*60*2)))
            y[z][G] = y[z][G] + longflare[flareMinute] # add flares swapped to second but not changing the name intrtoduces fewer bugs


    y = np.asarray(y)
    date,amplitude,mag,error,filts = [],[],[],[],[]
    for z in range(1, len(y)):
        if objectmag[z] > sat[z] and objectmag[z] < lim[z]:
            date.extend(obs[z])
            amplitude = y[z] + random.gauss(0,magUncertainy(zeroPoints[z],objectmag[z],30,background,FWHMeff[z]))
            mag.extend(objectmag[z] - amplitude)
            error.extend([sigSys + magUncertainy(zeroPoints[z],objectmag[z],30,background,FWHMeff[z])+0.2]*len(amplitude))
            filts.extend([filterletter[z]]*len(amplitude))
            
    date = np.asarray(date)
    mag = np.asarray(mag)
    filts = np.asarray(filts)
    error = np.asarray(error)

    f = open(miscFile,'r')
    stringaroni = f.read()
    f.close()
    newString = stringaroni + '\n\ndate = '+str(date)+'\n\nmag = '+str(mag)+'\n\nerror = '+str(error)+'\n\nfilts = '+str(filts)
    f = open(miscFile,'w')
    f.write(newString)
    f.close()
    
    model = periodic.LombScargleMultibandFast(fit_period=False)
    model.optimizer.period_range=(0.003, 26)
    model.fit(date, mag, error, filts)
    
    LSperiod = model.best_period

    freqs = fmin + df * np.arange(numsteps) 
    power = model.score_frequency_grid(fmin, df, numsteps) 
    maxpowerlow = power.max()
    #position = np.where(power==maxpowerlow)

    mpower = power.max()
    measuredpower.append(mpower) # should this correspond to period power and not max power?
    maxpower = []           
    counter = 0.
    for loop in range(loopNo):
        random.shuffle(date)
        model = periodic.LombScargleMultibandFast(fit_period=False)
        model.fit(date, mag, error, filts)
        power = model.score_frequency_grid(fmin, df, numsteps)  
        maxpower.append(power.max())

    for X in range(len(maxpower)):
        if maxpower[X] > measuredpower[-1]:
            counter = counter + 1. 
    Significance = (1.-(counter/len(maxpower)))
    SigLevel.append(Significance)
    
    results[0] = objectmag[3]
    results[1] = period
    results[2] = LSperiod
    results[3] = Significance
    results[4] = mpower
    results[5] = 0#listnumber
    return results


PrangeLoop = np.logspace(-2.5,1.4,freqlength)
FrangeLoop = [(1/x) for x in PrangeLoop]

with open(inFile,'w') as f:
    f.write('fullmaglist \n\n periodlist \n\n measuredperiodlist \n\n siglist \n\n powerlist \n\n listnumberlist \n\n end of file')

obs = np.asarray(obs)
for x in range(len(obs)):
    obs[x] = np.asarray(obs[x])

results = []
#newlist = Magnitudes.
newlist = Magnitudes.mag630

for h in range(startnumber,endnumber):
    for i in range(secondstartnumber,secondendnumber):
	results.append(lombScargle(FrangeLoop[i],objectmag=newlist[h],numsteps=500000)) 
    twoDlist = [[],[],[],[],[],[]]
    print(results)
    for X in range(len(results)):
        #for Y in range(len(results[X])):
        twoDlist[0].append(results[X][0])
        twoDlist[1].append(results[X][1])
        twoDlist[2].append(results[X][2])
        twoDlist[3].append(results[X][3])
        twoDlist[4].append(results[X][4])
        twoDlist[5].append(results[X][5])
    with open(inFile, 'r') as istr:
        with open(outFile,'w') as ostr:
            for i, line in enumerate(istr):
                # Get rid of the trailing newline (if any).
                line = line.rstrip('\n')
                if i % 2 != 0:
                    line += str(twoDlist[int((i-1)/2)])+','
                ostr.write(line+'\n')

    f = open(outFile[:-4]+'alt.txt','w')
    outString = 'objectmag = '+str(results[X][0])+'\nperiod = '+str(results[X][1])+'\nLSperiod = '+str(results[X][2])+'\nSignificance = '+str(results[X][3])+'\nmpower = '+str(results[X][4])+'\nlistnumber = '+str(results[X][5])
    f.write(outString)
    f.close()

