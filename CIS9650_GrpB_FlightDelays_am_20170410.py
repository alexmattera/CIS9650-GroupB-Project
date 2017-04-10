# -*- coding: utf-8 -*-
"""
CIS 9650
Group B
Project

Initial code to load and analyze flight delay data from
Kaggle dataset found at the following address:
https://www.kaggle.com/usdot/flight-delays
you need to download the flights.csv, airlines.csv, airports.csv
files to the home directory before running this script

A data dictionary that looks to explain a lot of these
codes can be found at:
https://www.transtats.bts.gov/Fields.asp?Table_ID=236

Alex Mattera
"""

import csv

###open file
f = open("flights.csv")
rows = csv.reader(f)
next(rows) #skip first line

###create class to store flight record values 
class flightRecord:
    YEAR = 0
    MONTH = 0
    DAY = 0
    DAY_OF_WEEK = 0
    AIRLINE_CODE = "" #for consistency, to match to airline name later
    FLIGHT_NUMBER = ""
    TAIL_NUMBER = ""
    ORIGIN_AIRPORT_CODE = ""
    DESTINATION_AIRPORT_CODE = ""
    SCHEDULED_DEPARTURE = 0
    DEPARTURE_TIME = 0
    DEPARTURE_DELAY = 0
    TAXI_OUT = 0
    WHEELS_OFF = 0
    SCHEDULED_TIME = 0
    ELAPSED_TIME = 0
    AIR_TIME = 0
    DISTANCE = 0
    WHEELS_ON = 0
    TAXI_IN = 0
    SCHEDULED_ARRIVAL = 0
    ARRIVAL_TIME = 0
    ARRIVAL_DELAY = 0
    DIVERTED = 0
    CANCELLED = 0
    CANCELLATION_REASON = ""
    AIR_SYSTEM_DELAY = 0
    SECURITY_DELAY = 0
    AIRLINE_DELAY = 0
    LATE_AIRCRAFT_DELAY = 0
    WEATHER_DELAY = 0

fdata = []

###iterate through file, create list of flightRecord objects
for row in rows:   
    fr = flightRecord()
    
    fr.YEAR = int(row[0])
    fr.MONTH = int(row[1])
    fr.DAY = int(row[2])
    fr.DAY_OF_WEEK = int(row[3])
    fr.AIRLINE_CODE = row[4]
    fr.FLIGHT_NUMBER = row[5]
    fr.TAIL_NUMBER = row[6]
    fr.ORIGIN_AIRPORT_CODE = row[7]
    fr.DESTINATION_AIRPORT_CODE = row[8]
    fr.SCHEDULED_DEPARTURE = int(row[9])
    fr.DEPARTURE_TIME = row[10]
    if row[11] != "":
        fr.DEPARTURE_DELAY = int(row[11])
    fr.TAXI_OUT = row[12]
    fr.WHEELS_OFF = row[13]
    fr.SCHEDULED_TIME = row[14]
    fr.ELAPSED_TIME = row[15]
    fr.AIR_TIME = row[16]
    fr.DISTANCE = row[17]
    fr.WHEELS_ON = row[18]
    fr.TAXI_IN = row[19]
    fr.SCHEDULED_ARRIVAL = row[20]
    fr.ARRIVAL_TIME = row[21]
    if row[22] != "":
        fr.ARRIVAL_DELAY = int(row[22])
    fr.DIVERTED = int(row[23])    
    fr.CANCELLED = int(row[24])
    fr.CANCELLATION_REASON = row[25]
    fr.AIR_SYSTEM_DELAY = row[26]
    fr.SECURITY_DELAY = row[27]
    fr.AIRLINE_DELAY = row[28]
    fr.LATE_AIRCRAFT_DELAY = row[29]
    fr.WEATHER_DELAY = row[30]
    
    fdata.append(fr)

f.close()

###open file
f = open("airlines.csv")
rows = csv.reader(f)
next(rows) #skip first line

###create class to store airline data
class Airline:
    AIRLINE_CODE = ""
    AIRLINE = ""

aldata = []

for row in rows:
    ar = Airline()
    
    ar.AIRLINE_CODE = row[0]
    ar.AIRLINE = row[1]
    
    aldata.append(ar)

f.close()

###open file
f = open("airports.csv")
rows = csv.reader(f)
next(rows) #skip first line

###create class to store airport data
class Airport:
    AIRPORT_CODE = ""
    AIRPORT = ""
    CITY = ""
    STATE = ""
    COUNTRY = ""
    LATITUDE = 0.0
    LONGITUDE = 0.0
    
apdata = []

for row in rows:
    ap = Airport()
    
    ap.AIRPORT_CODE = row[0]
    ap.AIRPORT = row[1]
    ap.CITY = row[2]
    ap.STATE = row[3]
    ap.COUNTRY = row[4]
    if row[5] != "" and row[6] != "":
        ap.LATITUDE = float(row[5])
        ap.LONGITUDE = float(row[6])
    
    apdata.append(ap)
    
f.close()

###function to display summary statistics for a list of flight records
def flightRecordSummary(fdata):
    print("\nData set represents " + str(len(fdata)) + " flights.")
    print("Of those " + str(len(list(filter(lambda x: x.DIVERTED == 1, fdata)))) + " flights were diverted")
    print("and " + str(len(list(filter(lambda x: x.CANCELLED == 1, fdata)))) + " flights were cancelled.")
    depdelays = list(map(lambda x: x.DEPARTURE_DELAY, fdata))
    print("The average departure delay was " + str(sum(depdelays)/len(depdelays)) + " minutes")
    arrdelays = list(map(lambda x: x.ARRIVAL_DELAY, fdata))
    print("and the average arrival delay was " + str(sum(arrdelays)/len(arrdelays)) + " minutes.")

###function to recursively subset data for delay prediction, expanding search until
###more than 10 records are found or search is expanded 6 times
def findSubset(fdata, searchOap, searchDap, searchAir, searchMonth, searchDofW, searchSchedDep, tDiff):
    #calculate boundary values
    lowDep = searchSchedDep - tDiff
    highDep = searchSchedDep + tDiff
    
    subdata =  list(filter(lambda x: x.AIRLINE_CODE == searchAir and x.ORIGIN_AIRPORT_CODE == searchOap and x.DESTINATION_AIRPORT_CODE == searchDap and 
                          x.MONTH == searchMonth and x.DAY_OF_WEEK == searchDofW and x.SCHEDULED_DEPARTURE <= highDep and x.SCHEDULED_DEPARTURE >= lowDep, fdata))
   
    if len(subdata) >= 10 or tDiff > 600:
        #sufficient number of records or search too wide
        return subdata
    else:
        #widen search
        tDiff += 100  #increment 1 hour
        return findSubset(fdata, searchOap, searchDap, searchAir, searchMonth, searchDofW, searchSchedDep, tDiff)

###function to find the best and worst airports based on departure delays
def bestAndWorstPort(fdata, apdata):
    #running variable to store best and worst airports data
    best = ""
    besttm = 0
    worst = ""
    worsttm = 1
    
    
    print("\nCalculating...\n") #so the user knows its working
    
    #iterate through airports
    for airport in apdata:
        flights = len(list(filter(lambda x: x.ORIGIN_AIRPORT_CODE == airport.AIRPORT_CODE, fdata)))
        delayed = len(list(filter(lambda x: x.ORIGIN_AIRPORT_CODE == airport.AIRPORT_CODE and x.DEPARTURE_DELAY > 0, fdata)))
        
        if flights == 0:
            #not valid for timeliness calculation if they have no departing flights
            continue
        else:
            #calculate timeliness and adjust running variables as necessary
            tm = delayed/flights
            if tm < worsttm:
                worst = airport.AIRPORT
                worsttm = tm
            if tm > besttm:
                best = airport.AIRPORT
                besttm = tm
        
    print ("The best airport is " + best + "\nwith an on-time record of " + str(besttm * 100) + "%.")
    print ("The worst airport is " + worst + "\nwith an on-time record of " + str(worsttm * 100) + "%.\n")

###function to find the best and worst airlines based on oeverall delays
def bestAndWorstLine(fdata, aldata):
    #running variable to store best and worst airports data
    best = ""
    besttm = 0
    worst = ""
    worsttm = 1
    
    print("\nCalculating...\n") #so the user knows its working
    
    #iterate through airlines
    for airline in aldata:
        flights = len(list(filter(lambda x: x.AIRLINE_CODE == airline.AIRLINE_CODE, fdata)))
        delayed = len(list(filter(lambda x: x.AIRLINE_CODE == airline.AIRLINE_CODE and (x.DEPARTURE_DELAY > 0 or x.ARRIVAL_DELAY > 0), fdata)))
        
        #calculate timeliness and adjust running variables as necessary
        tm = delayed/flights
        if tm < worsttm:
            worst = airline.AIRLINE
            worsttm = tm
        if tm > besttm:
            best = airline.AIRLINE
            besttm = tm
        
    print ("The best airline is " + best + "\nwith an on-time record of " + str(besttm * 100) + "%.")
    print ("The worst airline is " + worst + "\nwith an on-time record of " + str(worsttm * 100) + "%.\n")
        
###function to predict delays based on known flight data
def predictDelay(fdata):
    print("\nWelcome to the Flight Delay Predictive Model\n============================================\n")
    #read in search values from user
    searchOap = input("What airport will you be leaving from? (example: JFK): ")
    searchDap = input("What airport will you be flying to? (example: LAX): ")
    searchAir = input("Which airline are you flying? (example: B6): ")
    searchMonth = int(input("Which month will you be flying? (example: 1 = January, etc): "))
    searchDofW = int(input("Which day of the week will you be flying? (example: 1 = Monday, etc): "))
    searchSchedDep = int(input("What time is your flight scheduled to depart? (example: 800 = 8:00am, 2000 = 8:00pm): "))
    print("\nSearching...\n")   
    
    #calculate initial time difference
    tDiff = 100  # 1 hour
    
    #call function to subset data
    subdata = findSubset(fdata, searchOap, searchDap, searchAir, searchMonth, searchDofW, searchSchedDep, tDiff)
    
    if len(subdata) == 0:
        #no records returned
        print("Sorry, but no records were found for those search parameters.\nPlease try again\n")
    else:    
        #calculate and report average delays
        depdelays = list(map(lambda x: x.DEPARTURE_DELAY, subdata))
        arrdelays = list(map(lambda x: x.ARRIVAL_DELAY, subdata))        
        print("Based on the predictive model,\nyou can expect an average departure delay of " + str(sum(depdelays)/len(depdelays)) + " minutes")
        print("and an average arrival delay of " + str(sum(arrdelays)/len(arrdelays)) + " minutes.  Have a great flight!\n")

###main program
while(1):
    
    print("\nMain Menu\nChoose One:\n1 - Summary Statistics All Data\n2 - Summary Statistics by Airline\n3 - Summary Statistics by Origin Airport\n4 - Best and Worst\n5 - Predict Delay\n0 - Exit")
    i = input("What would you like to do? (0 - 5): ")
    if i == "1":
        ###Summary stats for all data
        print("\nSummary Statistics for all Airlines\n===================================")
        flightRecordSummary(fdata)
    elif i == "2":
        ###Airline Summary stats
        print("\nSummary Statistics by Airline\n=============================")
        print("1 - Show All Airlines\n2 - Show Specific Airline\n0 - Return to Main Menu\n")
        j = input("What is your choice? (0 - 2): ")
        if j == "1":
            #all airlines
            for airline in aldata:
                print("\n" + airline.AIRLINE + ":\n")
                #call function for subset of data
                flightRecordSummary(list(filter(lambda x: x.AIRLINE_CODE == airline.AIRLINE_CODE, fdata)))
        elif j == "2":
            #a particular airline
            searchLine = input("What airline would you like to see? (example: B6): ")
            print("\n" + list(filter(lambda x: x.AIRLINE_CODE == searchLine, aldata))[0].AIRLINE)
            flightRecordSummary(list(filter(lambda x: x.AIRLINE_CODE == searchLine, fdata)))
        else:
            continue        
    elif i == "3":
        ###Summary stats by origin airport
        print("\nSummary Statistics by Origin Airport\n=======================================\n")
        print("1 - Show All Airports\n2 - Show Specific Airport\n0 - Return to Main Menu\n")
        j = input("What is your choice? (0 - 2): ")
        if j == "1":
            #all airports
            for airport in apdata:
                print("\n" + airport.AIRPORT + ":\n")
                #call function for subset of data
                subdata = list(filter(lambda x: x.ORIGIN_AIRPORT_CODE == airport.AIRPORT_CODE, fdata))
                if len(subdata) > 0:
                    flightRecordSummary(subdata)
        elif j == "2":
            #a particular airport
            searchPort = input("What airport would you like to see? (example: JFK): ")
            print("\n" + list(filter(lambda x: x.AIRPORT_CODE == searchPort, apdata))[0].AIRPORT)
            flightRecordSummary(list(filter(lambda x: x.ORIGIN_AIRPORT_CODE == searchPort, fdata)))
        else:
            continue
    elif i == "4":
        print("\nBest and Worst\n==============\n")
        print("1 - See Best and Worst Airports by Departure Delays\n2 - See Best and Worst Airlines by Overall Delays\n0 - Return to Main Menu\n")
        j = input("What is your choice? (0 - 2): ")
        if j == "1":
            bestAndWorstPort(fdata, apdata)
        elif j == "2":
            bestAndWorstLine(fdata, aldata)
        else:
            continue
    elif i == "5":
        ###predict delay based on known flight data
        predictDelay(fdata)
    else:
        break
    
    

























