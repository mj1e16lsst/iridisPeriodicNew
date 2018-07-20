from operator import add
#from astropy import units as u
#from astropy.coordinates import SkyCoord
#from astropy.stats import LombScargle
#from gatspy.periodic import LombScargleFast
from functools import partial
#from gatspy import periodic
#import matplotlib.pyplot as plt
#from matplotlib.font_manager import FontProperties
import lomb_scargle_multiband as periodic
from multiprocessing import Pool
import numpy as np
import os
#from sqlite3 import *
import random
from random import shuffle
from random import randint
import Observations
import Magnitudes

# In[13]:


#conn = connect('minion_1016_sqlite.db')
#conn = connect('astro_lsst_01_1004_sqlite.db')
#conn = connect('minion_1020_sqlite.db')


# In[14]:


# LSST zero points  u,g,r,i,z,y
zeroPoints = [0,26.5,28.3,28.13,27.79,27.4,26.58]
FWHMeff = [0.8,0.92,0.87,0.83,0.80,0.78,0.76] # arcmins?
pixelScale = 0.2
readOut = 12.7
sigSys = 0.005
flareperiod = 4096
flarecycles = 10
dayinsec=86400
background = 40
# sat mag u,g,r,i,z,y=14.7,15.7,15.8,15.8,15.3 and 13.9
# start date 59580.033829 end date + 10 years
#maglist=[20]*7

lim = [0, 23.5, 24.8, 24.4, 23.9, 23.3, 22.1] # limiting magnitude ugry
sat = [0, 14.7, 15.7, 15.8, 15.8, 15.3, 13.9] # sat mag as above


# In[15]:


looooops = 10000
maglength = 20
freqlength = 20
processors = 20

startnumber = 0 + 15                  
endnumber = startnumber + 1

#observingStrategy = 'minion'
observingStrategy = 'astroD'
#observingStrategy = 'panstars'



inFile = '/home/mj1e16/periodic/in'+str(startnumber)+'.txt'
outFile = '/home/mj1e16/periodic/outbaseline630'+str(startnumber)+'.txt'

#inFile = '/home/ubuntu/vagrant/'+observingStrategy+'/in'+observingStrategy+'KtypefullresultsFile'+str(startnumber)+'.txt'
#outFile = '/home/ubuntu/vagrant/'+observingStrategy+'/out'+observingStrategy+'KtypefullresultsFile'+str(startnumber)+'.txt'


obs = Observations.obsbaseline630

# In[19]:


def magUncertainy(Filter, objectmag, exposuretime,background, FWHM): # b is background counts per pixel   
    countsPS = 10**((Filter-objectmag)/2.5)
    counts = countsPS * exposuretime
    uncertainty = 1/(counts/((counts/2.3)+(((background/2.3)+(12.7**2))*2.266*((FWHM/0.2)**2)))**0.5) # gain assumed to be 1
    return uncertainty
#from lsst should have got the website! https://smtn-002.lsst.io/


# In[20]:


def averageFlux(observations, Frequency, exptime):
    b = [0]*len(observations)
    for seconds in range(0, exptime):
        a = [np.sin((2*np.pi*(Frequency))*(x+(seconds/(3600*24)))) for x in observations] # optical modulation
        b = map(add, a, b)
    c = [z/exptime for z in b]
    return c

def Flux(observations,Frequency,exptime):
    a = [np.sin((2*np.pi*(Frequency)*x)) for x in observations]
    return a


# In[21]:


def ellipsoidalFlux(observations, Frequency,exptime):
    period = 1/(Frequency)
    phase = [(x % (2*period)) for x in observations]
    b = [0]*len(observations)
    for seconds in range(0, exptime):
        a = [np.sin((2*np.pi*(Frequency))*(x+(seconds/(3600*24)))) for x in observations] # optical modulation
        b = map(add, a, b)
    c = [z/exptime for z in b]
    
    for x in range(0,len(phase)):
        if (phase[x]+(1.5*period)) < (3*period):
            c[x] = c[x]*(1./3.)
        else:
            c[x] = c[x]*(2./3.)
    return c
## this is doing something but not the right something, come back to it 


# In[22]:


def flaring(B, length, dayinsec=86400,amplitude=1):   
    global flareMag, minutes
    fouriers = np.linspace(0.00001,0.05,(dayinsec/30))
    logF = [np.log(x) for x in fouriers] # start at 30 go to a day in 30 sec increments
    real = [random.gauss(0,1)*((1/x)**(B/2)) for x in fouriers] #random.gauss(mu,sigma) to change for values from zurita
    # imaginary = [random.gauss(0,1)*((1/x)**(B/2)) for x in fouriers]
    IFT = np.fft.ifft(real)
    seconds = np.linspace(0,dayinsec, (dayinsec/30)) # the day in 30 sec increments
    minutes = [x for x in seconds]
    minimum = (np.max(-IFT))
    positive = [x + minimum for x in IFT] # what did this even achieve? it helped with normalisation!
    normalised = [x/(np.mean(positive)) for x in positive] # find normalisation
    normalisedmin = minimum/(np.mean(positive))
    normalised = [x - normalisedmin for x in normalised]
    flareMag = [amplitude * x for x in normalised] # normalise to amplitude
    logmins = [np.log(d) for d in minutes] # for plotting?
#     plt.plot(minutes,flareMag)
#     plt.title('lightcurve')
#     plt.show()
    return flareMag


# In[55]:


def lombScargle(frequencyRange,objectmag=20,loopNo=looooops,df=0.001,fmin=0.001,numsteps=100000,modulationAmplitude=0.1,Nquist=200): # frequency range and object mag in list
    #global totperiod, totmperiod, totpower, date, amplitude, frequency, periods, LSperiod, power, mag, error, SigLevel
    results = {}
    totperiod = []
    totmperiod = []
    totpower = [] # reset
    SigLevel = []
    filterletter = ['o','u','g','r','i','z','y']
    
    period = 1/(frequencyRange)
    if period > 0.5:
        numsteps = 10000
    elif period > 0.01:
        numsteps = 100000
    else:
        numsteps = 200000
    freqs = fmin + df * np.arange(numsteps) # for manuel
    allobsy, uobsy, gobsy, robsy, iobsy, zobsy, yobsy = [], [], [], [], [], [], [] #reset
    measuredpower = [] # reset
    y = [allobsy, uobsy, gobsy, robsy, iobsy, zobsy, yobsy] # for looping only
    for z in range(1, len(y)):
        #y[z] = averageFlux(obs[z], frequencyRange[frange], 30)  # amplitde calculation for observations, anf frequency range
        y[z] = ellipsoidalFlux(obs[z], frequencyRange,30)
        y[z] = [modulationAmplitude * t for t in y[z]] # scaling
        for G in range(0, len(y[z])):
            flareMinute = int(round((obs[z][G]*24*60*2)%((dayinsec/(30*2))*flarecycles)))
            y[z][G] = y[z][G] + longflare[flareMinute] # add flares swapped to second but not changing the name intrtoduces fewer bugs
    date = []
    amplitude = []
    mag = []
    error = []
    filts = []
    for z in range(1, len(y)):
        if objectmag[z] > sat[z] and objectmag[z] < lim[z]:
            #date.extend([x for x in obs[z]])
            date.extend(obs[z])
            amplitude = [t + random.gauss(0,magUncertainy(zeroPoints[z],objectmag[z],30,background,FWHMeff[z])) for t in y[z]] # scale amplitude and add poisson noise
            mag.extend([objectmag[z] - t for t in amplitude]) # add actual mag
            error.extend([sigSys + magUncertainy(zeroPoints[z],objectmag[z],30,background,FWHMeff[z])+0.2]*len(amplitude))
            filts.extend([filterletter[z]]*len(amplitude))

            phase = [(day % (period*2))/(period*2) for day in obs[z]]
            pmag = [objectmag[z] - t for t in amplitude]
#         plt.plot(phase, pmag, 'o', markersize=4)
#         plt.xlabel('Phase')
#         plt.ylabel('Magnitude')
#         plt.gca().invert_yaxis()
#         plt.title('filter'+str(z)+', Period = '+str(period))#+', MeasuredPeriod = '+str(LSperiod)+', Periodx20 = '+(str(period*20)))
#         plt.show()

#     plt.plot(date, mag, 'o')
#     plt.xlim(lower,higher)
#     plt.xlabel('time (days)')
#     plt.ylabel('mag')
#     plt.gca().invert_yaxis()
#     plt.show()

    model = periodic.LombScargleMultibandFast(fit_period=False)
    model.fit(date, mag, error, filts)
    power = model.score_frequency_grid(fmin, df, numsteps) 

    if period > 10.:
        model.optimizer.period_range=(10, 110)
    elif period > 0.51:
        model.optimizer.period_range=(0.5, 10)
    elif period > 0.011:
        model.optimizer.period_range=(0.01, 0.52)
    else:
        model.optimizer.period_range=(0.0029, 0.012)


    LSperiod = model.best_period
    if period < 10:
        higher = 10
    else:
        higher = 100
#     fig, ax = plt.subplots()
#     ax.plot(1./freqs, power)
#     ax.set(xlim=(0, higher), ylim=(0, 1.2),
#            xlabel='period (days)',
#            ylabel='Lomb-Scargle Power',
#           title='Period = '+str(period)+', MeasuredPeriod = '+str(LSperiod)+', Periodx20 = '+(str(period*20)));
#     plt.show()


    phase = [(day % (period*2))/(period*2) for day in date]
    #idealphase = [(day % (period*2))/(period*2) for day in dayZ]
    #print(len(phase),len(idealphase))
    #plt.plot(idealphase,Zmag,'ko',)
#     plt.plot(phase, mag, 'o', markersize=4)
#     plt.xlabel('Phase')
#     plt.ylabel('Magnitude')
#     plt.gca().invert_yaxis()
#     plt.title('Period = '+str(period)+', MeasuredPeriod = '+str(LSperiod)+', Periodx20 = '+(str(period*20)))
#     plt.show()
    #print(period, LSperiod, period*20)

#         print('actualperiod', period, 'measured period', np.mean(LSperiod),power.max())# 'power',np.mean(power[maxpos]))
#         print(frequencyRange[frange], 'z', z)

#     totperiod.append(period)
#     totmperiod.append(np.mean(LSperiod))
#     totpower.append(power.max())
    mpower = power.max()
    measuredpower.append(power.max()) # should this correspond to period power and not max power?
    maxpower = []           
    counter = 0.
    for loop in range(0,loopNo):
        random.shuffle(date)
        model = periodic.LombScargleMultibandFast(fit_period=False)
        model.fit(date, mag, error, filts)
        power = model.score_frequency_grid(fmin, df, numsteps)  
        maxpower.append(power.max())


    for X in range(0, len(maxpower)):
        if maxpower[X] > measuredpower[-1]:
            counter = counter + 1. 
    Significance = (1.-(counter/len(maxpower)))
    #print('sig', Significance, 'counter', counter)
    SigLevel.append(Significance)
    
    #freqnumber = FrangeLoop.index(frequencyRange)
    #magnumber = MagRange.index(objectmag)
    #print(fullmaglist)
    #listnumber = (magnumber*maglength)+freqnumber
#     print(listnumber)
#     measuredperiodlist[listnumber] = LSperiod
#     periodlist[listnumber] = period
#     powerlist[listnumber] = mpower
#     siglist[listnumber] = Significance
#     fullmaglist[listnumber] = objectmag
# results order, 0=mag,1=period,2=measuredperiod,3=siglevel,4=power,5=listnumber
    results[0] = objectmag[3]
    results[1] = period
    results[2] = LSperiod
    results[3] = Significance
    results[4] = mpower
    results[5] = 0#listnumber
    return results


# In[24]:


#findObservations([(630,)])
#remove25(obs)
#averageFlux(obs[0], 1, 30)
longflare = []
for floop in range(0,flarecycles):
    flareone = flaring(-1, flareperiod, amplitude=0.3)
    flareone = flareone[0:1440]
    positiveflare = [abs(x) for x in flareone]
    longflare.extend(positiveflare)
    


# In[25]:


PrangeLoop = np.logspace(-2.5,2,freqlength)
FrangeLoop = [(1/x) for x in PrangeLoop]


# In[26]:


# reset results file
with open(inFile,'w') as f:
    f.write('fullmaglist \n\n periodlist \n\n measuredperiodlist \n\n siglist \n\n powerlist \n\n listnumberlist \n\n end of file')


# In[57]:


results = []
fullmeasuredPeriod = []
fullPeriod = []
fullPower = []
fullSigLevel = []
fullMag = []
MagRangearray = np.linspace(17,24,maglength)
MagRange = [x for x in MagRangearray]
maglist = []
for x in range(len(MagRange)):
    maglist.append([MagRange[x]]*7)


newlist = Magnitudes.mag630

pool = Pool(processors)
for h in range(startnumber,endnumber):
    print(newlist[h])
    results.append(pool.map(partial(lombScargle, objectmag=newlist[h]),FrangeLoop))
    
    twoDlist = [[],[],[],[],[],[]]
    for X in range(len(results)):
        for Y in range(len(results[X])):
            twoDlist[0].append(results[X][Y][0])
            twoDlist[1].append(results[X][Y][1])
            twoDlist[2].append(results[X][Y][2])
            twoDlist[3].append(results[X][Y][3])
            twoDlist[4].append(results[X][Y][4])
            twoDlist[5].append(results[X][Y][5])
    with open(inFile, 'r') as istr:
        with open(outFile,'w') as ostr:
            for i, line in enumerate(istr):
                # Get rid of the trailing newline (if any).
                line = line.rstrip('\n')
                if i % 2 != 0:
                    line += str(twoDlist[int((i-1)/2)])+','
                ostr.write(line+'\n')

