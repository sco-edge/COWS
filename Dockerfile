# Python 3.9 슬림 이미지를 기반으로 사용
# 슬림 이미지는 기본 이미지보다 크기가 작아 빌드 시간과 이미지 크기를 줄일 수 있습니다.
FROM python:3.9-slim

# 작업 디렉토리를 /app으로 설정
# 이는 애플리케이션 코드가 컨테이너 내부에서 위치할 디렉토리입니다.
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
# gcc: Python 패키지 컴파일에 필요
# curl: 헬스체크에 사용
# 설치 후 apt 캐시를 정리하여 이미지 크기를 줄입니다.
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일을 컨테이너로 복사
# requirements.txt에는 Flask, requests, prometheus-client 등이 포함되어 있습니다.
COPY requirements.txt .

# Python 패키지 설치
# --no-cache-dir: pip 캐시를 사용하지 않아 이미지 크기를 줄입니다.
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드를 컨테이너로 복사
# app.py는 각 서비스의 Flask 애플리케이션 파일입니다.
COPY app.py .

# 컨테이너가 사용할 포트를 노출
# 9080 포트는 각 서비스의 HTTP 서버가 사용하는 포트입니다.
EXPOSE 9080

# 헬스체크 설정
# 컨테이너가 정상적으로 작동하는지 확인하기 위한 헬스체크를 설정합니다.
# --interval=30s: 30초마다 체크
# --timeout=3s: 3초 내에 응답이 없으면 실패
# --start-period=5s: 컨테이너 시작 후 5초 동안은 헬스체크를 하지 않음
# --retries=3: 3번 실패하면 컨테이너를 비정상으로 간주
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9080/health || exit 1

# 컨테이너 시작 시 실행할 명령어
# Python으로 app.py를 실행하여 Flask 서버를 시작합니다.
CMD ["python", "app.py"] 