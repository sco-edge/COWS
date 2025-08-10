# Ubuntu 환경 설정 가이드

## 🌐 언어 설정
- **한글 언어 설정**: [한글 언어 설정 가이드](https://ahnbk.dev/?p=368)

## 🖥️ 기본 도구 설치

### 웹 브라우저
```bash
# 크롬 설치
sudo apt install wget -y
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i ./google-chrome-stable_current_amd64.deb
```

### 텍스트 에디터
```bash
# nano 에디터 설치
sudo apt-get install nano
```

### 유틸리티 도구
```bash
# 압축 해제 도구
sudo apt-get install unzip

# 네트워크 정보 확인
sudo apt-get install net-tools

# 로그 분석 도구
sudo apt-get install multitail
```

## 🔒 보안 설정

### SSH 접속 허용
```bash
# SSH 포트(22) 허용
sudo iptables -I INPUT -p tcp --dport 22 -j ACCEPT

# SSL/SFTP 포트 허용 (포트 번호는 필요에 따라 변경)
sudo iptables -I INPUT -p tcp --dport [포트번호] -j ACCEPT
```

## 🖥️ 가상화 도구

### VMware 설치
- **VMware Player 다운로드**: [VMware 공식 다운로드 페이지](https://softwareupdate.vmware.com/cds/vmw-desktop/player/)

## ☸️ 컨테이너 오케스트레이션

### 쿠버네티스 설치
- **Ubuntu 22.04 쿠버네티스 설치 가이드**: [Velog 가이드](https://velog.io/@fill0006/Ubuntu-22.04-%EC%BF%A0%EB%B2%84%EB%84%A4%ED%8B%B0%EC%8A%A4-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0)

---

> 💡 **참고**: 모든 명령어는 Ubuntu 환경에서 실행됨. 다른 배포판을 사용하는 경우 패키지 매니저 명령어가 다를 수 음
