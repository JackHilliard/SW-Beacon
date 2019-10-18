from lib.queries import sql
import time
from sqlite3 import Error
from lib.config import conf
from lib.DB import DB
from lib.BTScanner import BLEScanner
import signal
import re
import sys
import os
import subprocess

# Scanning get all of the mac from the db & save readings for the mac address that are in the beacon table
'''
1. Select all beacons address in beacon table 
2. scan for all 
3. Save readings only for mac addresses that are in the beacon table 
'''
#decode rssi
def twos_comp(val, bits):
    if ((val & (1 << (bits - 1))) != 0):
        val = val - (1 << bits)
    return val

class BLEBeacon:
    def __init__(self, id, macAddr):
        self.id = id
        self.macAddr = macAddr
        self.combRssi = 0
        self.countRssi = 0
        self.avgRssi = 0

def save_data(connection, timestamp):
    now = int(round((timestamp+15) * 1000)) 
    scanner = BLEScanner()
    scanner.start()
    cur = connection.cursor()
    cur.execute(sql['getBeacons'])
    db_beacons = cur.fetchall()
    beacons = []
    for db_beacon in db_beacons:
        beacons.append(BLEBeacon(db_beacon['id'], db_beacon['mac']))
    print('Scanning LE devices (' + str(conf['scanInterval']) + 's)')
    currentTime = time.time()
    for line in scanner.get_lines():
        if line:
            found_mac = line[14:][:12]
            reversed_mac = ''.join(
                reversed([found_mac[i:i + 2] for i in range(0, len(found_mac), 2)]))
            mac = ':'.join(a+b for a,b in zip(reversed_mac[::2], reversed_mac[1::2]))
            data = line[26:]
            #cycle through all the known beacons
            for x in range(len(beacons)):
                if mac == beacons[x].macAddr:
                    #print(mac, data)
                    #average reading
                    beacons[x].combRssi+=twos_comp(int(data[-2:],16), 8)
                    beacons[x].countRssi+=1
                    break
        if(time.time() >= currentTime + conf['averageInterval']): #if it goes 15 seconds timeout
            break
        
    scanner.stop()
    for beacon in beacons:
        #print('Found:', beacon.macAddr, 'Count:', beacon.countRssi)
        if beacon.countRssi != 0:
            beacon.avgRssi = round(beacon.combRssi/beacon.countRssi)
            #now = int(round(time.time() * 1000))
            cur = connection.cursor()
            cur.execute(sql['insertReading'], (beacon.avgRssi, now, 'NEW', beacon.id))

    try:
        connection.commit()
        print('Saved new scans.')
    except Error as e:
        print (e)


def run():
    conn = DB().getConn()
    while conn:
        timeNow = time.time()
        if ((round(timeNow) % 15) == 0):
            save_data(conn, round(timeNow))
