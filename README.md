# SW-Beacon
Raspberry Pi software to detect beacons transmitting advertising data and detect their RSSI.

Setup guide:

#install libraries
sudo apt-get install python-pip
sudo apt-get sqlite3
sudo apt-get install pip
sudo pip install requests
sudo pip install lib
sudo pip install requests
sudo apt-get install libglib2.0-dev
sudo pip install bluepy==1.1.1
sudo apt-get install netatalk
sudo apt-get install git build-essential libglib2.0-dev
sudo apt-get install libcap2-bin
sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/local/lib/python2.7/dist-packages/bluepy/bluepy-helper

cd /home/pi/

#setup database:
sudo mkdir sw-database
mv /home/pi/sw-code/empty-db.sqlite /home/pi/sw-database/smartward.sqlite
sudo sqlite3 sw-database/smartward.sqlite
CREATE TABLE Beacon_Readings (id_Readings INTEGER PRIMARY KEY autoincrement, rssi INTEGER NOT NULL, mac_FK INTEGER NOT NULL, timestamp INTEGER NOT NULL, state TEXT DEFAULT 'NEW');
CREATE TABLE Beacons (id INTEGER PRIMARY KEY autoincrement, mac TEXT NOT NULL, active TEXT DEFAULT 'TRUE');

#move config file
mv /home/pi/sw-code/example.config.json /home/pi/sw-config/config.json

#setup service
sudo echo "[Unit]
Description=SmartWard Beacon Scanner Service
 
[Service]
User=pi
Group=pi
ExecStart=/usr/bin/python -u /home/pi/sw-code/__main__.py
Environment=CONFIG=/home/pi/sw-config/config.json
Restart=on-failure
RestartSec=3
StandardOutput=journal
StandardError=journal
 
[Install]
WantedBy=multi-user.target
Alias=sw-beacon.service" > /lib/systemd/system/sw-beacon.service
