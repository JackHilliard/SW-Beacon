sql = {
    "getNewReadings": 'SELECT br.id_Readings, b.mac, br.rssi, br.timestamp FROM Beacons AS b JOIN Beacon_Readings AS br ON (br.mac_FK = b.id AND br.state = "NEW") LIMIT 400',
    "retryReadings": 'SELECT br.id_Readings, b.mac, br.rssi, br.timestamp FROM Beacons AS b JOIN Beacon_Readings AS br ON (br.mac_FK = b.id AND br.state = "FAILED") LIMIT 400',
    "getBeacons": 'SELECT id, mac FROM Beacons WHERE active = "TRUE"',
    "deleteReading": 'DELETE FROM Beacon_Readings WHERE id_Readings=?',
    "insertBeacon": 'INSERT INTO Beacons (mac) VALUES (?)',
    "deleteBeacon": 'DELETE FROM Beacons WHERE mac=?',
    "setFailed": 'UPDATE Beacon_Readings SET state="FAILED" WHERE id_Readings=?',
    "insertReading": 'INSERT INTO Beacon_Readings (rssi,timestamp,state, mac_FK) VALUES (?,?,?,?)'
}
