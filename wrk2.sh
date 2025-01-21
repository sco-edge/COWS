sudo apt-get update
sudo apt-get install build-essential libssl-dev git
git clone https://github.com/giltene/wrk2.git

### 애플 실리콘 환경에는 Rosetta 2 설치 필요
sudo softwareupdate --install-rosetta

cd wrk2
make clean && make

### path 설정
sudo cp wrk /usr/local/bin

