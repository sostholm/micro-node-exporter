
sudo adduser micro-node-exporter --disabled-login
sudo mkdir /home/micro-node-exporter/micro-node-exporter
sudo cp app.py /home/micro-node-exporter/micro-node-exporter
sudo chown micro-node-exporter /home/micro-node-exporter/micro-node-exporter/app.py
sudo cp micro-node-exporter.service /etc/systemd/system/
sudo -u micro-node-exporter /usr/bin/python3 -m pip install -r requirements.txt
sudo systemctl enable micro-node-exporter
sudo systmectl start micro-node-exporter
