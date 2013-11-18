# dsr.zip must contain the contents of the python directory

# you can run a sample python webserver to serve up dsr.zip
# using `python -m http.server 80`


cd ~/Deployment
rm dsr.zip

wget "http://10.1.1.200/dsr.zip"
cd ~/DSR
./stop.sh
cd ~/Deployment
rm -rf ~/DSR
mkdir ~/DSR
unzip dsr.zip -d ~/DSR
chmod +x ~/DSR/stop.sh
chmod +x ~/DSR/start.sh

cd ~/DSR
./start.sh >~/DSRlog/`date "+%s"`.log 2>&1 &
