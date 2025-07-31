# Extended Bookinfo - Istio 마이크로서비스 확장 프로젝트

## 📋 프로젝트 개요

이 프로젝트는 Istio의 기본 Bookinfo 샘플 애플리케이션을 확장하여 10개의 추가 Python 마이크로서비스를 포함한 도서관 관리 시스템입니다.

## 🏗️ 아키텍처

### 기존 Bookinfo 서비스
- **productpage**: 메인 페이지 (기존)
- **details**: 도서 상세 정보 (기존)
- **reviews**: 리뷰 서비스 (기존)
- **ratings**: 평점 서비스 (기존)

### 추가된 마이크로서비스 (10개)
1. **user-service**: 사용자 관리 (포트: 30082)
2. **order-service**: 주문 관리 (포트: 30085)
3. **catalog-service**: 카탈로그 관리 (포트: 30083)
4. **inventory-service**: 재고 관리 (포트: 30086)
5. **payment-service**: 결제 시스템 (포트: 30087)
6. **notification-service**: 알림 서비스 (포트: 30088)
7. **search-service**: 검색 서비스 (포트: 30084)
8. **recommendation-service**: 추천 시스템 (포트: 30089)
9. **analytics-service**: 분석 서비스 (포트: 30090)
10. **shipping-service**: 배송 관리 (포트: 30091)

### 통합 포털
- **library-portal**: 모든 서비스에 접근할 수 있는 통합 포털 (포트: 30081)

## 🚀 배포 방법

### 1. 사전 요구사항

```bash
# Minikube 설치 (아직 설치하지 않은 경우)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Istio 설치 (아직 설치하지 않은 경우)
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.23.0
export PATH=$PWD/bin:$PATH
```

### 2. Minikube 클러스터 시작

```bash
# Minikube 클러스터 시작 (Istio 프로필 사용)
minikube start -p istiotest --driver=docker --cpus=4 --memory=8192

# Minikube Docker 환경 설정 (중요!)
eval $(minikube docker-env -p istiotest)

# 클러스터 상태 확인
kubectl cluster-info
```

### 3. Istio 설치 및 설정

```bash
# Istio 설치
istioctl install --set profile=demo -y

# 네임스페이스에 Istio 자동 주입 활성화
kubectl label namespace default istio-injection=enabled

# Istio 애드온 설치 (선택사항)
kubectl apply -f samples/addons
kubectl rollout status deployment/kiali -n istio-system
```

### 4. 프로젝트 배포

```bash
# 프로젝트 디렉토리로 이동
cd extended-bookinfo

# 모든 서비스 배포
./deploy.sh

# 배포 상태 확인
kubectl get pods -n extended-bookinfo
kubectl get services -n extended-bookinfo
```

### 5. 서비스 접근

```bash
# Minikube IP 확인
minikube ip -p istiotest

# 포털 접근 (브라우저에서)
http://$(minikube ip -p istiotest):30081

# 개별 서비스 접근
http://$(minikube ip -p istiotest):30082  # User Service
http://$(minikube ip -p istiotest):30085  # Order Service
http://$(minikube ip -p istiotest):30083  # Catalog Service
# ... 기타 서비스들
```

## 🔧 주요 스크립트 설명

### deploy.sh
```bash
#!/bin/bash
# 전체 애플리케이션 배포 스크립트

# 1. 네임스페이스 생성
kubectl create namespace extended-bookinfo

# 2. Istio 자동 주입 활성화
kubectl label namespace extended-bookinfo istio-injection=enabled

# 3. 기본 Bookinfo 배포
kubectl apply -f ../bookinfo.yaml

# 4. 확장 서비스들 배포
kubectl apply -f k8s-manifests.yaml

# 5. NodePort 서비스 배포 (외부 접근용)
kubectl apply -f nodeport-services.yaml
```

### build-images.sh
```bash
#!/bin/bash
# Docker 이미지 빌드 스크립트

# Minikube Docker 환경 설정
eval $(minikube docker-env -p istiotest)

# 각 서비스별 이미지 빌드
docker build -t extended-bookinfo/user-service:latest user-service/
docker build -t extended-bookinfo/order-service:latest order-service/
# ... 기타 서비스들
```

### cleanup.sh
```bash
#!/bin/bash
# 배포된 리소스 정리 스크립트

# 네임스페이스 삭제 (모든 리소스 함께 삭제)
kubectl delete namespace extended-bookinfo

# 기본 Bookinfo 삭제
kubectl delete -f ../bookinfo.yaml
```

## 📁 파일 구조

```
extended-bookinfo/
├── README.md                    # 이 파일
├── deploy.sh                    # 배포 스크립트
├── build-images.sh              # 이미지 빌드 스크립트
├── cleanup.sh                   # 정리 스크립트
├── requirements.txt              # Python 의존성
├── Dockerfile                   # 공통 Docker 설정
├── k8s-manifests.yaml           # Kubernetes 매니페스트
├── nodeport-services.yaml       # NodePort 서비스 설정
├── library-portal/              # 통합 포털
│   └── app.py
├── user-service/                # 사용자 관리 서비스
│   └── app.py
├── order-service/               # 주문 관리 서비스
│   └── app.py
├── catalog-service/             # 카탈로그 관리 서비스
│   └── app.py
├── inventory-service/           # 재고 관리 서비스
│   └── app.py
├── payment-service/             # 결제 시스템
│   └── app.py
├── notification-service/        # 알림 서비스
│   └── app.py
├── search-service/              # 검색 서비스
│   └── app.py
├── recommendation-service/      # 추천 시스템
│   └── app.py
├── analytics-service/           # 분석 서비스
│   └── app.py
└── shipping-service/            # 배송 관리 서비스
    └── app.py
```

## 🐳 Docker 이미지 빌드

### 개별 서비스 빌드
```bash
# 특정 서비스만 빌드
eval $(minikube docker-env -p istiotest)
docker build -t extended-bookinfo/user-service:latest user-service/
```

### 전체 서비스 빌드
```bash
# 모든 서비스 빌드
./build-images.sh
```

### 캐시 없이 강제 빌드 (UI 업데이트 시)
```bash
# 캐시를 사용하지 않고 완전히 새로 빌드
docker build --no-cache -t extended-bookinfo/user-service:latest user-service/
```

## ☸️ Kubernetes 배포

### 매니페스트 파일 설명

#### k8s-manifests.yaml
```yaml
# 각 서비스별 Kubernetes 리소스 정의
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: extended-bookinfo
spec:
  ports:
  - port: 9080
    targetPort: 9080
    protocol: TCP
  selector:
    app: user-service-v1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service-v1
  namespace: extended-bookinfo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: user-service-v1
  template:
    metadata:
      labels:
        app: user-service-v1
        version: v1
    spec:
      containers:
      - name: user-service
        image: extended-bookinfo/user-service:latest
        ports:
        - containerPort: 9080
```

#### nodeport-services.yaml
```yaml
# 외부 접근을 위한 NodePort 서비스 정의
apiVersion: v1
kind: Service
metadata:
  name: user-service-nodeport
  namespace: extended-bookinfo
spec:
  type: NodePort
  ports:
  - port: 9080
    targetPort: 9080
    nodePort: 30082  # 외부 접근 포트
    protocol: TCP
  selector:
    app: user-service-v1
```

## 🔄 서비스 업데이트

### 코드 변경 후 재배포
```bash
# 1. 이미지 재빌드
eval $(minikube docker-env -p istiotest)
docker build --no-cache -t extended-bookinfo/user-service:latest user-service/

# 2. 파드 강제 삭제 (새 이미지 적용)
kubectl delete pod -l app=user-service-v1 -n extended-bookinfo

# 3. 새 파드 생성 확인
kubectl get pods -n extended-bookinfo | grep user-service
```

### 롤아웃 재시작
```bash
# 배포 재시작 (간단한 방법)
kubectl rollout restart deployment/user-service-v1 -n extended-bookinfo
```

## 🌐 Istio 적용

### 1. Virtual Service 설정
```yaml
# istio-virtual-services.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: user-service-vs
  namespace: extended-bookinfo
spec:
  hosts:
  - user-service
  http:
  - route:
    - destination:
        host: user-service
        port:
          number: 9080
```

### 2. Destination Rule 설정
```yaml
# istio-destination-rules.yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: user-service-dr
  namespace: extended-bookinfo
spec:
  host: user-service
  subsets:
  - name: v1
    labels:
      version: v1
```

### 3. Istio 적용
```bash
# Virtual Service 적용
kubectl apply -f istio-virtual-services.yaml

# Destination Rule 적용
kubectl apply -f istio-destination-rules.yaml

# Istio 설정 확인
istioctl analyze -n extended-bookinfo
```

## 🔍 서비스 포워딩

### 포트 포워딩 방법

#### 1. kubectl port-forward (개발용)
```bash
# User Service 포워딩
kubectl port-forward -n extended-bookinfo svc/user-service 9080:9080

# Order Service 포워딩
kubectl port-forward -n extended-bookinfo svc/order-service 9080:9080

# 브라우저에서 접근: http://localhost:9080
```

#### 2. NodePort 사용 (프로덕션용)
```bash
# NodePort 서비스 확인
kubectl get svc -n extended-bookinfo | grep nodeport

# Minikube IP로 접근
minikube ip -p istiotest
# 브라우저에서: http://<minikube-ip>:30082
```

#### 3. LoadBalancer 사용 (클라우드 환경)
```bash
# LoadBalancer 서비스 생성
kubectl expose deployment user-service-v1 -n extended-bookinfo --type=LoadBalancer --port=9080

# 외부 IP 확인
kubectl get svc -n extended-bookinfo
```

## 📊 모니터링 및 로그

### 로그 확인
```bash
# 특정 서비스 로그
kubectl logs -f deployment/user-service-v1 -n extended-bookinfo

# 모든 파드 로그
kubectl logs -f -l app=user-service-v1 -n extended-bookinfo
```

### 상태 확인
```bash
# 파드 상태
kubectl get pods -n extended-bookinfo

# 서비스 상태
kubectl get svc -n extended-bookinfo

# 이벤트 확인
kubectl get events -n extended-bookinfo --sort-by='.lastTimestamp'
```

### Istio 모니터링
```bash
# Kiali 대시보드 접근
istioctl dashboard kiali

# Grafana 대시보드 접근
istioctl dashboard grafana

# Jaeger 트레이싱 접근
istioctl dashboard jaeger
```

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. ImagePullBackOff 오류
```bash
# Minikube Docker 환경 확인
eval $(minikube docker-env -p istiotest)

# 이미지 재빌드
docker build --no-cache -t extended-bookinfo/user-service:latest user-service/

# 파드 강제 삭제
kubectl delete pod -l app=user-service-v1 -n extended-bookinfo
```

#### 2. 서비스 연결 실패
```bash
# 서비스 엔드포인트 확인
kubectl get endpoints -n extended-bookinfo

# 서비스 DNS 확인
kubectl run test --image=busybox --rm -it --restart=Never -- nslookup user-service
```

#### 3. 포트 충돌
```bash
# 사용 중인 포트 확인
kubectl get svc -n extended-bookinfo | grep NodePort

# 포트 변경 (nodeport-services.yaml 수정)
kubectl apply -f nodeport-services.yaml
```

## 📝 개발 가이드

### 새 서비스 추가
1. `service-name/` 디렉토리 생성
2. `app.py` 작성 (Flask 애플리케이션)
3. `k8s-manifests.yaml`에 서비스 정의 추가
4. `nodeport-services.yaml`에 NodePort 서비스 추가
5. Docker 이미지 빌드 및 배포

### UI 테마 변경
```css
.logo-icon {
    background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
}

.hero-title {
    background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

## 📞 지원

문제가 발생하거나 질문이 있으시면:
1. 로그 확인: `kubectl logs -f deployment/<service-name> -n extended-bookinfo`
2. 파드 상태 확인: `kubectl get pods -n extended-bookinfo`
3. 서비스 상태 확인: `kubectl get svc -n extended-bookinfo`

## 📄 라이선스

© 2025 Korea University NetLab JunhoBae. All rights reserved. 
