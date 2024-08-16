sudo apt-get update
sudo apt-get install build-essential libssl-dev git
git clone https://github.com/giltene/wrk2.git
cd wrk2
make
sudo cp wrk /usr/local/bin/wrk2

