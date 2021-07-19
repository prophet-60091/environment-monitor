# environment-monitor

setting up grafana on the pi-server
https://grafana.com/docs/grafana/latest/installation/debian/
sudo nano /etc/apt/sources.list
(add the following line)
deb https://packages.grafana.com/oss/deb stable main
(exit and save)
sudo apt-get update
sudo apt-get install grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
sudo systemctl status grafana-server
<pi-serverip>:3000 (in my case 192.168.178.18:3000)
https://grafana.com/docs/grafana/latest/getting-started/getting-started/
admin/admin is default first time password, make a new one
add data source
url is our pi server ip + port
auth = basic auth
add admin creds
add database name "environments"
add admin user and pass
test



###################################
setting up the raspberry pi 0 node
 connect keyboard, monitor, power
 log in first with 
 username pi
 password raspberry
 then run sudo raspi-config
 under system options, add the wifi, change the password, change the hostname
 under interface options enable ssh and i2c
  sudo reboot -f     (!!! Important, you've changed the hostname but it hasn't updated yet, need to reboot for changes to apply. stuff won't work until you do!)

 run sudo raspi-config then update
 Finish and exit raspi-config

 required libraries (install as sudo as service will run as sudo)
sudo apt-get install p7zip-full
sudo apt install git
sudo apt-get install python3-pip 
sudo apt-get install python3-smbus
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
sudo pip3 install Pillow
sudo pip3 install adafruit-circuitpython-sgp30
sudo pip3 install influxdb
mkdir code
mkdir waveshare
 cd code
 git clone https://github.com/prophet-60091/environment-monitor.git
 cd environment-monitor
 nano node_code
 change path of .SHTC3.so to /home/pi/code/environment-monitor/SHTC3.so
 cd 
 cd waveshare
 wget https://www.waveshare.com/w/upload/6/6c/Sense-HAT-B-Demo.7z


 7z x Sense-HAT-B-Demo.7z

#INSTALL NEEDED LIBRARIES for Sense Hat
#BCM2835 library
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
sudo tar zxvf bcm2835-1.60.tar.gz
cd bcm2835-1.xx
sudo ./configure
sudo make
sudo make check
sudo make install

#wiringPi libraries  #!!!! do not follow waveshare guide, see here http://wiringpi.com/download-and-install/
sudo apt-get install wiringpi

# "i2cdetect -y 1" - detects hardware address of i2c devices

######################################################

Service for the Script
Now we're going to define the service to run this script:

cd /lib/systemd/system/
sudo nano environment-monitor.service
The service definition must be on the /lib/systemd/system folder. Our service is going to be called "environment-monitor.service":
##################


[Unit]
Description=environment-monitor
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/code/environment-monitor/node_code.py
Restart=always

[Install]
WantedBy=multi-user.target





#################
sudo chmod 644 /lib/systemd/system/environment-monitor.service
chmod +x /home/pi/code/environment-monitor/node_code.py
sudo systemctl daemon-reload
sudo systemctl enable environment-monitor.service
sudo systemctl start environment-monitor.
sudo systemctl status environment-monitor.service



