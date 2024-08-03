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

쿠버네티스 설치
https://velog.io/@fill0006/Ubuntu-22.04-%EC%BF%A0%EB%B2%84%EB%84%A4%ED%8B%B0%EC%8A%A4-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0
