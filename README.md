# Micro Node Exporter
Is designed to export basic metrics from a server using the top command, exporting it through the prometheus http server.

run by: 
pip install -r requirements.txt
python app.py


# Install as systemd service
- create a new user: sudo adduser micro-node-exporter --disable-login