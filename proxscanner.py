#!/usr/bin/python

import subprocess
import bluetooth
import time
import requests

def main():
    print "Bluetooth Proximity Scanner with Authentication"
    print "By Martin Fredriksson (martinfredriksson.com)"
    
    proxScanner = ProxScanner()
    proxScanner.run()    

class ProxScanner(object):
    
    # SETTINGS #
    username1 = "Martin"
    authentication = True
    mac = ""
    url = ""
    scanDelay = 10
    failThresh = 5
    command = "hcitool cc " + mac + " && hcitool auth " + mac + " && hcitool dc " + mac
    
    # Init Variables
    authenticated = False
    disconnects = 0

    def __init__(self):
        pass

    def sendUpdate(self, status):
        if status == False:
           val = "OFF"
        else:
           val = "ON"
        while True:
            try:
                r= requests.post("URLHERE", data=val.encode('utf-8'), headers={'Content-type' : 'text/plain; charset=utf-8'})
                print ("Successfully updated with API request")
            except Exception as e:
                print("Failed to connect to API, retrying....")
                time.sleep(5)
                continue
            break


    def run(self):
        while True:
            print "Looking for device at " + time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
            result = bluetooth.lookup_name('MACADR', timeout=5)
            if (result != None):
                if self.authenticated == False and self.authentication == True:
                    #Need to authenticate
                    print self.username1 + ": Probably in, not authenticated, try authentication"
                    try:
                        output = subprocess.check_output(self.command, stderr=subprocess.STDOUT, shell=True)
                        self.authenticated = True
                        self.disconnects = 0
                        print self.username1 + ": Successfully authenticated"
                        self.sendUpdate(True)
                    except subprocess.CalledProcessError as e:
                        print self.username1 + ": Auth Failed"
                        print(e)
                else:
                #Already authenticated OR no need for authentication
                    self.disconnects = 0
                    if self.authentication == True:
                        print self.username1 + ": Not left since last authentication, keep status as authenticated"
                    else: 
                       print self.username1 + ": Authentication disabled, don't care about authentication"
            else:
                self.disconnects +=1
                print self.username1 + ": Not nearby for " + str(self.disconnects) + " probes, " + str(self.failThresh - self.disconnects) + " until deauth"
                if(self.disconnects == self.failThresh):
                    print "Deauth"
                    self.authenticated = False
                    self.sendUpdate(False)
            if(self.authenticated == True):
                time.sleep(self.scanDelay)
            else:
                time.sleep(1)
main()
