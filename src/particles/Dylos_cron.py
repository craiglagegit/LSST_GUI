#!/usr/bin/env python
#Author: Craig Lage, Andrew Bradshaw, Perry Gee, UC Davis; 
#Date: 17-Feb-15
# These files contains various subroutines
# needed to run the LSST Simulator
# This class interfaces to the Dylos 1100 Pro Particle Counter.

# Using the Tkinter module for interface design
import matplotlib
matplotlib.use("Agg")
import numpy, time, datetime, sys, os, serial, struct, subprocess, urllib2
from pylab import *
sys.path.append('/sandbox/lsst/lsst/GUI')
import eolib
import Lakeshore_335
import DewarFill
import Email_Warning
#************************************* SUBROUTINES ***********************************************

class Dylos(object):
    def __init__(self):
        self.dylos_device_name='/dev/dylos'
        self.particle_small = 999999
        self.particle_big = 999999
        return

    def Initialize_Serial(self):
        """ Initializes the USB serial bus, using the python serial module"""
        try:
            self.ser = serial.Serial(self.dylos_device_name, 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
            self.ser.close()
            self.ser.open()
            print "Successfully initialized Dylos Particle Counter\n"
            sys.stdout.flush()
            return
        except Exception as e:
            print "Failed to initialize Dylos. Exception of type %s and args = \n"%type(e).__name__, e.args    
            sys.stdout.flush()
            return

    def Close_Serial(self):
        """ Closes the USB serial bus, using the python serial module"""
        try:
            self.ser.close()
            print "Successfully closed Dylos Serial Bus\n"
            sys.stdout.flush()
            return
        except Exception as e:
            print "Failed to close Dylos Serial Bus. Exception of type %s and args = \n"%type(e).__name__, e.args    
            sys.stdout.flush()
            return

    def Check_Communications(self):
        """ Checks whether communication with the Dylos is working"""
        self.comm_status = False
        try:
            self.comm_status = self.ser.isOpen()
        except Exception as e:
            print "Failed to set Dylos Comm Status. Exception of type %s and args = \n"%type(e).__name__, e.args    
            self.comm_status = False
        return

    def Read_Dylos(self):
        """ Reads the particle count value. """
        self.particle_big = 999999
        self.particle_small = 999999
        try:
            if self.ser.isOpen():
                listen=[]
                self.ser.flushInput()
                while (len(listen) < 2 or len(listen) > 16):
                    time.sleep(0.1)
                    listen = self.ser.readline()
                listen = listen.strip('\r\n').split(',')
                self.particle_small = int(listen[0])
                self.particle_big = int(listen[1])
                print "Succeeded in reading Dylos. Small = %d, Big = %d\n"%(self.particle_small, self.particle_big)
                sys.stdout.flush()
        except Exception as e:
            print "Failed to read Dylos. Exception of type %s and args = \n"%type(e).__name__, e.args    
            sys.stdout.flush()
            self.particle_small = 999999
            self.particle_big = 999999
        return

def CheckIfFileExists(filename):
    try:
        FileSize = os.path.getsize(filename)
        return True
    except (OSError, IOError):
        return False

def Date_to_JD(DateTime):
    # Convert a datetime to Julian Day.
    # Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
    # 4th ed., Duffet-Smith and Zwart, 2011.
    # Assumes the date is after the start of the Gregorian calendar.
    year = DateTime.year
    month = DateTime.month
    day = DateTime.day

    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month

    # Assumes we are after the start of the Gregorian calendar
    A = numpy.trunc(yearp / 100.)
    B = 2 - A + numpy.trunc(A / 4.)
    C = numpy.trunc(365.25 * yearp)
    D = numpy.trunc(30.6001 * (monthp + 1))
    jd = B + C + D + day + 1720994.5

    return jd + (DateTime.hour + DateTime.minute / 60.0 + DateTime.second / 3600.0) / 24.0

def JD_to_Date(jd):
    # Convert a Julian Day to time and date
    jd = jd + 0.5
    F, I = math.modf(jd)
    I = int(I)
    A = math.trunc((I - 1867216.25)/36524.25)
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
    C = B + 1524
    D = math.trunc((C - 122.1) / 365.25)
    E = math.trunc(365.25 * D)
    G = math.trunc((C - E) / 30.6001)
    days = C - E + F - math.trunc(30.6001 * G)
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
    days, day = math.modf(days)
    hours = days * 24.
    hours, hour = math.modf(hours)
    mins = hours * 60.
    mins, min = math.modf(mins)
    secs = mins * 60.
    secs, sec = math.modf(secs)
    return (int(year), int(month), int(day), int(hour), int(min), int(sec))

def GetLastNLines(filename, n):
    # Get last n lines of a file
    proc=subprocess.Popen(['tail','-n',str(n),filename], stdout=subprocess.PIPE)
    soutput,sinput=proc.communicate()
    lines = soutput.split('\n')
    lines.pop() # Strip last line, which is empty
    return lines

def GetExteriorCounts():
    ExtTime = []
    Ext = []
    DateTime = datetime.datetime.now()
    try:
        response = urllib2.urlopen('http://www.arb.ca.gov/aqmis2/display.php?download=y&param=PM25HR&units=001&year=2016&report=SITE1YR&statistic=DAVG&site=2143&ptype=aqd&monitor=-', timeout=10)
        data = response.read()
        response.close()
    except Exception as e:
        print "Failed to read Exterior particle counts. Exception of type %s and args = \n"%type(e).__name__, e.args    
        sys.stdout.flush()
        return (ExtTime, Ext)
    lines = data.split('\r\n')
    for line in lines:
        entries = line.split(',')
        try:
            date = entries[0].split('-')
            year = int(date[0])
            month = int(date[1])
            day = int(date[2])
            counts = float(entries[3])
            ExtTime.append(Date_to_JD(datetime.datetime(year,month,day,21,43,0)))
            Ext.append(counts / 6.5E-5)
        except (EOFError, ArithmeticError, ValueError, IndexError):
            continue
    return (ExtTime, Ext)

def ReadParticleLog(filename):
    cuft_per_cum = (39.37/12.0)**3
    lines = GetLastNLines(filename, 1500)
    Time = []
    Small = []
    Big = []
    for i, line in enumerate(lines):
        data = line.split()
        Time.append(float(data[0]))
        Small.append(int(data[1]) * cuft_per_cum)
        Big.append(int(data[2]) * cuft_per_cum)
    return(Time, Small, Big)

def ReadTemperatureLog(filename):
    lines = GetLastNLines(filename, 1500)
    Time = []
    Temp_A = []
    Temp_B = []
    for i, line in enumerate(lines):
        data = line.split()
        Time.append(float(data[0]))
        Temp_A.append(float(data[1]))
        Temp_B.append(float(data[2]))
    return(Time, Temp_A, Temp_B)


def MakePlot(Time, Small, Big, ExtTime, Ext, TempTime, Time_A, Time_B):
    # Moving averages
    Big_Ave = []
    Small_Ave = []
    NAve = 12
    for i in range(len(Big)):
        Big_Ave.append((array(Big[i-NAve+2:i]).sum() + Big[i-1] + Big[i])/NAve + 100.0)
        Small_Ave.append(max(Small[i], 3000.0))
    (year, month, day, hour, min, sec) = JD_to_Date(Time[-1])
    MinTime = Time[-1]-9.0
    MaxTime = MinTime + 10.0
    MinY = 0.0
    MaxY = 7.0
    figure(figsize=(8,10))
    ax1=axes([0.2,0.35,0.7,0.55])
    ax1.set_title("Particle Count Trend - Horizontal Dashed Lines are Class 1000")
    ax1.set_xlabel("Time (Julian Day)")
    #ylabel("Log Particles/m^3")
    ax1.text(MinTime-0.9,4.5,"Log Particles/m^3", color='black', rotation = 'vertical')
    ax1.text(MinTime-0.5,3.3,">2.5 $\mu m$", color='green', rotation = 'vertical')
    ax1.text(MinTime-0.5,4.7,">0.5 $\mu m$", color='blue', rotation = 'vertical')
    ax1.set_ylim(MinY,MaxY)
    ax1.set_xlim(MinTime, MaxTime)
    ax1.plot(Time, log10(Small_Ave), marker = 'o', ms = 0.1, color='blue')
    ax1.plot([MinTime, MaxTime],log10([35200, 35200]),color='blue',ls='--',lw=2) # Class 1000 line
    #text(MinTime + 1.0, log10(15000), 'Class 1000 > 0.5 micron', color='blue', fontweight = 'bold')
    ax1.plot(Time, log10(Big_Ave), marker = 'o', ms = 0.1, color='green')
    ax1.plot(ExtTime, log10(Ext), marker = 'o', ms = 0.1, color='red')
    ax1.plot([MinTime, MaxTime],log10([1240, 1240]),color='green',ls='--',lw=2) # Class 1000 line
    #text(MinTime+1.0, log10(600), 'Class 1000 > 2.5 micron', color='green', fontweight = 'bold')
    ax1.text(MinTime+1.0, 1.5, 'Last measurement made at %02d:%02d:%02d on %d/%d/%d'%(hour,min,sec,month,day,year), color='blue', fontweight = 'bold')
    ax1.text(MinTime+1.0, 1.0, 'Exterior air quality from www.arb.ca.gov', color='red', fontweight = 'bold')
    #ax1.text(MinTime+1.0, 0.5, 'Temp_A = %.2f, Temp_B = %.2f'%(Temp_A[-1], Temp_B[-1]), color='blue', fontweight = 'bold')

    # Finish Marks
    for i in range(11):
        daytime = int(MinTime) + 0.5 + float(i)
        ax1.plot([daytime,daytime],[MinY,MaxY],linestyle = 'dotted', color = 'black')

    CfgFile = "/sandbox/lsst/lsst/GUI/UCDavis.cfg"
    Temp_to_Fill = float(eolib.getCfgVal(CfgFile,"Temp_to_Fill")) # This is the temp to trigger a fill

    ax2=axes([0.2,0.1,0.65,0.15])
    ax2.set_title("Temperature Trend")
    ax2.set_xlabel("Time (Julian Day)")
    ax2.set_ylabel("Dewar Temperature (C)", color='blue')
    ax2.plot([MinTime,MaxTime],[Temp_to_Fill,Temp_to_Fill],linestyle = 'dotted', color = 'red')
    MinY = -195.0
    MaxY = -192.0
    ax2.set_ylim(MinY,MaxY)
    ax2.set_xlim(MinTime, MaxTime)
    ax2.plot(TempTime, Temp_A, marker = 'o', ms = 0.1, color='blue')

    for i in range(11):
        daytime = int(MinTime) + 0.5 + float(i)
        ax2.plot([daytime,daytime],[MinY,MaxY],linestyle = 'dotted', color = 'black')

    fill_lines = GetLastNLines('fill_log.dat', 10) # Get last 10 fills
    for line in fill_lines:
        plottime = float(line.split()[0])
        if plottime > MinTime:
            ax2.plot([plottime, plottime],[-193.5, -193.0],color='brown', lw=3)
            ax2.text(plottime-0.30, -193.0, 'Fill', color='brown')
    ax3=ax2.twinx()
    ax3.set_ylim(-140,40)
    ax3.set_xlim(MinTime, MaxTime)
    ax3.set_ylabel("CCD Temperature (C)", color='green')
    ax3.plot(TempTime, Temp_B, marker = 'o', ms = 0.1, color='green')

    savefig("particle_graph.png")

    # Now transfer the graph to the physauth server
    try:
        command = 'scp particle_graph.png cslage@physauth:/physweb-sites/lage.physics.ucdavis.edu/support_files/astro_papers/'
        copygraph = subprocess.Popen(command, shell=True)
    except Exception as e:
        print "File transfer of particle graph failed. Exception of type %s and args = \n"%type(e).__name__, e.args    
        sys.stdout.flush()
    start = time.time()
    elapsed = 0.0
    while elapsed < 40.0:
        returncode = subprocess.Popen.poll(copygraph)
        elapsed = time.time() - start
        time.sleep(0.5)

    if returncode == None:
        print "File transfer of particle graph failed!"
        sys.stdout.flush()
    else:
        print "File transfer of particle graph succeeded!"
        sys.stdout.flush()
    return

def CheckIfStillRunning():
    # This checks if the last cron job is still running.
    # We don't want to keep launching jobs if the last one has hung up
    if CheckIfFileExists("DylosStillRunning"):
        print "Cron Job still running. Quitting\n"
        sys.stdout.flush()
        file = open('DylosStillRunning','r')
        line = file.readline()
        file.close()
        lastminute = int(line.split()[4].split(':')[1])
        currentminute = datetime.datetime.now().minute
        if currentminute - lastminute < 15:
            # Only send a warning the first time it fails so as not to spam inboxes.
            Email_Warning.Send_Warning('Dylos Cron Job Failure', 'Dylos particle cron job appears to have quit running.')
    file = open('DylosStillRunning','w')
    file.write("Job started at "+str(datetime.datetime.now())+" is still running\n")
    file.close()
    return

def ReadAndLogParticles():
    # Handles reading and logging the particle counts
    dylos = Dylos()
    dylos.Initialize_Serial()
    dylos.Read_Dylos()
    jd = Date_to_JD(datetime.datetime.now())
    out = "%.4f \t \t %d \t \t \t \t %d\n"%(jd, dylos.particle_small*100, dylos.particle_big*100)
    file = open('particle_log.dat', 'a')
    file.write(out)
    file.close()
    return

def ReadTempsAndHandleDewarFill(dewarfill):
    # Reads the temperatures and manages the Dewar fill
    lake = Lakeshore_335.Lakeshore('dummy')
    lake.Initialize_Serial()
    lake.Read_Temp()
    NumTries = 0
    # Added the following loop to prevent occasional bogus 999.0 readings
    while lake.Temp_A > 900.0 and NumTries < 5:
        time.sleep(0.5)
        lake.Read_Temp()
        NumTries += 1

    jd = Date_to_JD(datetime.datetime.now())
    out = "%.4f \t \t %.2f \t \t %.2f\n"%(jd, lake.Temp_A, lake.Temp_B)
    file = open('temperature_log.dat', 'a')
    file.write(out)
    file.close()

    # Dewar Autofill
    CfgFile = "/sandbox/lsst/lsst/GUI/UCDavis.cfg"
    # This file has the parameters that control the autofill
    Dewar_is_Cold = int(eolib.getCfgVal(CfgFile,"Dewar_is_Cold"))
    # Change this flag to turn off automatic Dewar fill and E-Mail warnings
    # 1 = Autofill enabled; 0 = autofill disabled
    Temp_to_Fill = float(eolib.getCfgVal(CfgFile,"Temp_to_Fill")) # This is the temp to trigger a fill
    Fill_Time_Limit = float(eolib.getCfgVal(CfgFile,"Fill_Time_Limit")) # This is the maximum fill time
    Overflow_Temp_Limit = float(eolib.getCfgVal(CfgFile,"Overflow_Temp_Limit"))
    # This is the temp on the overflow monitor that stops the fill

    if Dewar_is_Cold == 1 and lake.Temp_A > Temp_to_Fill:
        (TempTime, Temp_A, Temp_B) = ReadTemperatureLog('temperature_log.dat')
        if Temp_A[-1] > Temp_to_Fill - 0.2:
            lake.Read_Temp()
            NumTries = 0
            # Added the following loop to prevent occasional bogus 999.0 readings
            while lake.Temp_A > 900.0 and NumTries < 5:
                time.sleep(0.5)
                lake.Read_Temp()
                NumTries += 1
            if lake.Temp_A > Temp_to_Fill:
                # This sequence ensures that a fill only happens if
                # we have three readings in a row over the set point.
                # Now we also check that a fill has not occurred in the last 3 hours
                fill_lines = GetLastNLines('fill_log.dat', 1) # Get last fill
                if jd - float(fill_lines[0].split()[0]) > 0.125:
                    start_fill_status = dewarfill.StartFill()
                    time.sleep(0.1)
                    if start_fill_status:
                        time.sleep(0.1)
                        startfill = time.time()
                        elapsed = 0.0
                        temp = 25.0
                        overflowfile = open('overflow_log.dat','a')
                        time.sleep(0.1)
                        while elapsed < Fill_Time_Limit and temp > Overflow_Temp_Limit:
                            # Stop the fill when we reach time limit or detect LN2 overflow
                            # or detect that the valve is no longer open (open:state=True)
                            [state, temp] = dewarfill.MeasureOverFlowTemp()
                            line = "Temp at %s is %f\n"%(datetime.datetime.now(),temp)
                            overflowfile.write(line)
                            elapsed = time.time() - startfill
                            if state:
                                valve_state = "Open"
                            if not state:
                                # Break out of the loop if the valve doesn't stay open
                                valve_state = "Closed"
                                break
                            time.sleep(0.25)
                        if state:
                            dewarfill.LogFill()
                        print "Terminated fill loop. Elapsed = %f, Overflow temp = %f, Valve state = %s\n"%(elapsed,temp,valve_state) 
                        sys.stdout.flush()
                        overflowfile.close()
                    stop_fill_status = dewarfill.StopFill()
                    NumTries = 0
                    while not stop_fill_status and NumTries < 5: # Try 5 times to make sure valve is closed
                        time.sleep(0.5)
                        stop_fill_status = dewarfill.StopFill()
                        NumTries += 1
                    if not stop_fill_status:
                        Email_Warning.Send_Warning('Failure terminating Dewar fill!!!!')

    if Dewar_is_Cold == 1 and lake.Temp_A > -190.0:
        Email_Warning.Send_Warning('Dewar Temp Warning', 'Warning. Dewar Temp > -190 C')
    return

#************************************* MAIN PROGRAM ***********************************************
print "Starting. Current time = ", datetime.datetime.now()
sys.stdout.flush()
jd1 = Date_to_JD(datetime.datetime.now())
CheckIfStillRunning() # Make sure there isn't another job still running.

ReadAndLogParticles()
(Time, Small, Big) = ReadParticleLog('particle_log.dat')

dewarfill = DewarFill.DewarFill('dummy')
try:
    ReadTempsAndHandleDewarFill(dewarfill)
except Exception as e:
    print "Failure in Temp read or Dewar Fill. Exception of type %s and args = \n"%type(e).__name__, e.args    
    sys.stdout.flush()
    dewarfill.StopFill() # In case of failure, make sure dewar fill valve is closed
(TempTime, Temp_A, Temp_B) = ReadTemperatureLog('temperature_log.dat')
(ExtTime,Ext) = GetExteriorCounts()

MakePlot(Time, Small, Big, ExtTime, Ext, TempTime, Temp_A, Temp_B)

# Delete file which indicates we are still running.
command = "rm DylosStillRunning"
delfile = subprocess.Popen(command, shell=True)
subprocess.Popen.wait(delfile)
jd2 = Date_to_JD(datetime.datetime.now())
elapsed = (jd2-jd1)*86400
print "Current time = ", datetime.datetime.now()
print "Done. Elapsed time = %f\n"%elapsed
sys.stdout.flush()
#************************************* END MAIN PROGRAM ***********************************************
