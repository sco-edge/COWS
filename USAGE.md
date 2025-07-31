# Extended Bookinfo Application 사용법

이 가이드는 Istio의 기본 Bookinfo 샘플 애플리케이션을 확장한 버전의 사용법을 설명합니다.

## 📋 개요

기존 Bookinfo 애플리케이션(4개 서비스)에 10개의 추가 마이크로서비스를 파이썬으로 구현했습니다:

### 기존 서비스
- **productpage**: 메인 웹 페이지
- **details**: 도서 상세 정보
- **reviews**: 리뷰 서비스 (v1, v2, v3)
- **ratings**: 평점 서비스

### 추가된 서비스
1. **user-service**: 사용자 관리 및 인증
2. **order-service**: 주문 처리 및 관리
3. **inventory-service**: 재고 관리
4. **payment-service**: 결제 처리
5. **notification-service**: 알림 서비스
6. **search-service**: 도서 검색
7. **recommendation-service**: 추천 시스템
8. **analytics-service**: 사용자 행동 분석
9. **catalog-service**: 카탈로그 관리
10. **shipping-service**: 배송 관리

## 🚀 빠른 시작

### 1. 사전 요구사항
- Kubernetes 클러스터
- Istio 설치
- Docker
- kubectl

### 2. Docker 이미지 빌드
```bash
# 모든 서비스의 Docker 이미지를 빌드합니다
./build-images.sh
```

### 3. 애플리케이션 배포
```bash
# 확장된 Bookinfo 애플리케이션을 배포합니다
./deploy.sh
```

### 4. 배포 확인
```bash
# 모든 파드가 실행 중인지 확인
kubectl get pods -n extended-bookinfo

# 서비스 목록 확인
kubectl get services -n extended-bookinfo
```

## 🔧 서비스 테스트

### 기본 Bookinfo 접근
```bash
# Productpage 서비스에 포트포워딩
kubectl port-forward -n extended-bookinfo svc/productpage 9080:9080

# 브라우저에서 접근
open http://localhost:9080
```

### 확장된 서비스 테스트

#### User Service
```bash
kubectl port-forward -n extended-bookinfo svc/user-service 9081:9080
curl http://localhost:9081/users
curl http://localhost:9081/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"john_doe"}'
```

#### Order Service
```bash
kubectl port-forward -n extended-bookinfo svc/order-service 9082:9080
curl http://localhost:9082/orders
curl http://localhost:9082/orders -X POST -H "Content-Type: application/json" -d '{"user_id":"user1","items":[{"book_id":"book1","quantity":2,"price":29.99}]}'
```

#### Inventory Service
```bash
kubectl port-forward -n extended-bookinfo svc/inventory-service 9083:9080
curl http://localhost:9083/inventory
curl http://localhost:9083/inventory/book1
```

#### Search Service
```bash
kubectl port-forward -n extended-bookinfo svc/search-service 9084:9080
curl "http://localhost:9084/search?q=gatsby"
curl "http://localhost:9084/search?genre=fiction"
```

#### Analytics Service
```bash
kubectl port-forward -n extended-bookinfo svc/analytics-service 9085:9080
curl http://localhost:9085/analytics/summary
curl http://localhost:9085/analytics/track -X POST -H "Content-Type: application/json" -d '{"event_type":"page_view","user_id":"user1","metadata":{"page":"/productpage"}}'
```

## 📊 모니터링

### Prometheus 메트릭
각 서비스는 `/metrics` 엔드포인트를 통해 Prometheus 메트릭을 제공합니다:

```bash
# User Service 메트릭
curl http://localhost:9081/metrics

# Order Service 메트릭
curl http://localhost:9082/metrics
```

### 헬스체크
각 서비스는 `/health` 엔드포인트를 통해 헬스체크를 제공합니다:

```bash
curl http://localhost:9081/health
```

## 🔍 Istio 기능 활용

### 서비스 메시 시각화
```bash
# Kiali 대시보드 접근
kubectl port-forward -n istio-system svc/kiali 20001:20001
open http://localhost:20001
```

### 트래픽 관리
```bash
# Virtual Service 생성 예시
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: user-service-vs
spec:
  hosts:
  - user-service
  http:
  - route:
    - destination:
        host: user-service
        port:
          number: 9080
EOF
```

### 서킷 브레이커 설정
```bash
# Destination Rule 생성 예시
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: user-service-dr
spec:
  host: user-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1024
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
EOF
```

## 🧹 정리

애플리케이션을 정리하려면:

```bash
./cleanup.sh
```

## 📁 프로젝트 구조

```
extended-bookinfo/
├── README.md                 # 프로젝트 개요
├── USAGE.md                  # 사용법 가이드 (이 파일)
├── requirements.txt          # 공통 Python 의존성
├── k8s-manifests.yaml       # Kubernetes 매니페스트
├── deploy.sh                # 배포 스크립트
├── cleanup.sh               # 정리 스크립트
├── build-images.sh          # Docker 이미지 빌드 스크립트
├── user-service/            # 사용자 관리 서비스
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── order-service/           # 주문 처리 서비스
├── inventory-service/        # 재고 관리 서비스
├── payment-service/          # 결제 처리 서비스
├── notification-service/     # 알림 서비스
├── search-service/          # 도서 검색 서비스
├── recommendation-service/   # 추천 시스템 서비스
├── analytics-service/       # 사용자 행동 분석 서비스
├── catalog-service/         # 카탈로그 관리 서비스
└── shipping-service/        # 배송 관리 서비스
```

## 🔧 개발 및 확장

### 새 서비스 추가
1. 새 서비스 디렉토리 생성
2. `app.py` 작성 (Flask 기반)
3. `Dockerfile` 생성
4. `k8s-manifests.yaml`에 서비스 추가
5. `build-images.sh`에 서비스 추가

### 서비스 간 통신
서비스들은 HTTP를 통해 통신하며, Istio의 서비스 메시 기능을 활용할 수 있습니다:

```python
# 다른 서비스 호출 예시
import requests

# User Service에서 Order Service 호출
response = requests.get('http://order-service:9080/orders/user/user1')
```

## 🐛 문제 해결

### 일반적인 문제들

1. **파드가 시작되지 않는 경우**
   ```bash
   kubectl describe pod <pod-name> -n extended-bookinfo
   kubectl logs <pod-name> -n extended-bookinfo
   ```

2. **서비스 간 통신 문제**
   ```bash
   # Istio 사이드카 로그 확인
   kubectl logs <pod-name> -c istio-proxy -n extended-bookinfo
   ```

3. **메트릭 수집 문제**
   ```bash
   # Prometheus 설정 확인
   kubectl get prometheus -n istio-system
   ```

## 📚 추가 리소스

- [Istio 공식 문서](https://istio.io/latest/docs/)
- [Bookinfo 샘플 애플리케이션](https://istio.io/latest/docs/examples/bookinfo/)
- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [Flask 공식 문서](https://flask.palletsprojects.com/) 