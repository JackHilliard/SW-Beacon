from lib.queries import sql
import time
from sqlite3 import Error
from lib.BTScanner import scanner
from lib.config import conf
from lib.DB import DB
import signal

# Scanning get all of the mac from the db & save readings for the mac address that are in the beacon table
'''
1. Select all beacons address in beacon table 
2. scan for all 
3. Save readings only for mac addresses that are in the beacon table 
'''

class BLEBeacon:
    def __init__(self, macAddr):
        self.macAddr = macAddr
        self.combRssi = 0
        self.countRssi = 0
        self.avgRssi = 0

def macsOnly(beaconRow):
    return beaconRow['mac']


def save_data(connection):
    cur = connection.cursor()
    cur.execute(sql['getBeacons'])
    db_beacons = cur.fetchall()
    beacons = []
    for db_beacon in range(db_beacons)):
        beacons.append(BLEBeacon(db_beacon['mac']))
    print('Scanning LE devices (' + str(conf['scanInterval']) + 's)')
    discovered = scanner.scan(timeout=conf['scanInterval'])
    print('Finished scanning. Saw: ' + str([dev.addr.upper() for dev in discovered if dev.addr.upper() in map(macsOnly, db_beacons)]))
    for device in discovered:
        dev_mac = device.addr.upper()
        dev_rssi = device.rssi
        for beacon in beacons:
            if dev_mac == beacon.macAddr:
                beacon.combRssi+=dev_rssi
                beacon.countRssi+=1
                break
        
        #beacons = [db_beacon for db_beacon in db_beacons if db_beacon['mac'] == dev_mac]
    for beacon in beacons:
        if beacon.countRssi != 0:
            beacon.avgRssi = beacon.combRssi/beacon.countRssi
            now = int(round(time.time() * 1000))
            cur = connection.cursor()
            cur.execute(sql['insertReading'], (beacon.avgRssi, now, 'NEW', beacon.macAddr))

    try:
        connection.commit()
        print('Saved new scans.')
    except Error as e:
        print (e)


def run():
    conn = DB().getConn()
    while conn:
        save_data(conn)
