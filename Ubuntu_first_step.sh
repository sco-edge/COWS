한글 언어 설정
https://ahnbk.dev/?p=368

크롬 설치
sudo apt install wget -y
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i ./google-chrome-stable_current_amd64.deb

nano 에디터 설정
sudo apt-get install nano

unzip
sudo apt-get install unzip

ifconfig
sudo apt-get install net-tools

multitail (로그 분석)
sudo apt-get install multitail

SSH 허용
sudo iptables -I INPUT -p tcp --dport (SSL/SFTP용 포트) -j ACCEPT
iptables -I INPUT -p tcp --dport 22 -j ACCEPT

vmware 설치
