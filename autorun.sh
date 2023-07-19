#! usr/bin/bash
# navigate inside the repository
cd ~/Desktop/golem-slag
# try update repository
git pull || echo "no connection" 

echo "Check requirements"
pip install -r requirements.txt

echo "Config Bluetooth"
# some lines may not be required on each reboot
sudo hciconfig hci0 piscan
sudo systemctl daemon-reload
sudo service bluetooth restart
sudo sdptool add SP
sudo chmod o+rw /var/run/sdp
sudo hciconfig hci0 piscan

echo "run python"
python ~/Desktop/golem-slag/main.py

# == Do perform manualy only once ==
# add user to bluetooth group
# ~ sudo usermod -a -G bluetooth $USER
# In 'sudo nano /etc/systemd/system/bluetooth.target.wants/bluetooth.service' modify or add 'ExecStart=-/usr/lib/bluetooth/bluetoothd -- experimental'  
# restart bluetooth
# ~ sudo systemctl daemon-reload
# ~ sudo systemctl restart bluetooth.service
# ==========================
