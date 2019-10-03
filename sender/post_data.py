import requests
from requests.exceptions import ConnectionError
from lib.config import conf
from lib.queries import sql
from sqlite3 import Error
import time
from lib.DB import DB
import json


def post_data(connection):
    cur = connection.cursor()
    cur.execute(sql['getNewReadings'])
    scansFromDB = cur.fetchall()
    
    if (len(scansFromDB)==0):
        connection.commit()
        return

    cur2 = connection.cursor()
    cur2.execute(sql['getBeacons'])
    beaconsFromDB = cur2.fetchall()

    body = {
        "scans": [{"timestamp": scan['timestamp'], "mac": scan['mac'], "rssi": scan['rssi']} for scan in scansFromDB],
        "beacons": [db_beacon['mac'] for db_beacon in beaconsFromDB]
    }

    try:
        print('Sending: ' + str(len(scansFromDB)) + ' new scans')
        r = requests.post(conf['api']['url'] + conf['api']['dirs']['beacon'],
                          headers={"Authorization": "Bearer " + conf['api']['token'],
                                    "Content-Type": "application/json"},
                          json=body)
        print('Response: ' + str(r.status_code))
        if r.status_code == 200:
            for item in scansFromDB:
                # Remove uploaded scans from DB
                cur.execute(sql['deleteReading'], (item['id_Readings'],))

            received_data = r.json()
            add = received_data["add"]
            remove = received_data["remove"]

            # Add Functionality
            for mac in add:
                cur.execute(sql['insertBeacon'], (mac,))

            # Remove Functionality
            for mac in remove:
                cur.execute(sql['deleteBeacon'], (mac,))

        else:
            try:
                received_data = r.json()
                if received_data['errors']:
                    print('Errors:', json.dumps(received_data['errors']))
                else:
                    print('Response:', json.dumps(received_data))

                # Set scans to failed on DB
                for item in scansFromDB:
                    cur.execute(sql['setFailed'], (item['id_Readings'],))
            except ValueError as e:
                print(e)
                print('Response:', r.text)
        try:
            connection.commit()
            print('Updated beacons and scans in database.')
        except Error as e:
            print(e)
    except ConnectionError as e:
        print(e)
        for item in scansFromDB:
            cur.execute(sql['setFailed'], (item['id_Readings'],))

        connection.commit()


def run():
    conn = DB().getConn()
    while conn:
        post_data(conn)
        time.sleep(conf['sendInterval'])
