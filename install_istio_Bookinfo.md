# Bookinfo 애플리케이션 설치 가이드

## 1. 사전 요구사항 설치

### 1.1 Docker 설치
```bash
# Docker 설치
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64

# Docker 자동 실행 설정
sudo systemctl enable docker

# VirtualBox 설치 (Docker 미작동 시)
sudo apt install virtualbox
```

### 1.2 Minikube 설치 및 설정
```bash
# Minikube 프로필 생성 (bookinfo 이름으로)
minikube start -p bookinfo --memory 8192 --cpus 4

# 또는 기존 프로필 사용
minikube start -p new

# 프로필 확인
minikube profile list
minikube profile

# 환경변수 설정
export PATH="$PATH:/home/junho/Documents/istio-1.23.0/bin"
```

## 2. Istio 설치

### 2.1 Istio 다운로드
```bash
# 최신 버전 설치
curl -L https://istio.io/downloadIstio | sh -

# 또는 특정 버전 설치
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.6.8 TARGET_ARCH=x86_64 sh -

# Istio 디렉토리로 이동
cd istio-<version>
export PATH=$PWD/bin:$PATH
```

### 2.2 Istio 설치
```bash
# Istio 설치 (demo 프로필)
istioctl install --set profile=demo -y

# 네임스페이스에 Istio 사이드카 주입 활성화
kubectl label namespace default istio-injection=enabled
kubectl label namespace istio-system istio-injection=enabled
```

## 3. Bookinfo 애플리케이션 배포

### 3.1 Bookinfo 배포
```bash
# Bookinfo 애플리케이션 배포
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml

# 배포 확인
kubectl get services
kubectl get pods
```

### 3.2 Gateway 설정
```bash
# 애플리케이션 인그레스 게이트웨이 설정
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml

# 게이트웨이 IP 주소/포트 확인
kubectl get svc istio-ingressgateway -n istio-system
```

## 4. Observability 도구 설치 (선택사항)

### 4.1 기본 모니터링 도구 설치
```bash
cd samples/addons
kubectl apply -f jaeger.yaml
kubectl apply -f loki.yaml
kubectl apply -f grafana.yaml
kubectl apply -f kiali.yaml
kubectl apply -f prometheus.yaml

cd extras
kubectl apply -f zipkin.yaml
kubectl apply -f skywalking.yaml
```

### 4.2 OpenTelemetry 설정
```bash
# observability 네임스페이스 생성
kubectl delete namespace observability
kubectl create namespace observability

# observability 사이드카 주입
kubectl label namespace observability istio-injection=enabled

# OpenTelemetry 배포
kubectl delete -f samples/open-telemetry/otel.yaml -n observability
kubectl apply -f samples/open-telemetry/otel.yaml -n observability
```

## 5. 접근 및 확인

### 5.1 애플리케이션 접근
```bash
# 게이트웨이 IP 확인
kubectl get svc istio-ingressgateway -n istio-system

# 포트포워딩으로 접근
kubectl port-forward svc/istio-ingressgateway 8080:80 -n istio-system
```

### 5.2 Observability 도구 접근
```bash
# Kiali 대시보드
istioctl dashboard kiali

# Jaeger 대시보드
istioctl dashboard jaeger
kubectl -n istio-system port-forward deploy/jaeger 16686:16686

# Grafana 접근
while true; do kubectl -n istio-system port-forward deploy/grafana 3000:3000; done

# Prometheus 접근
while true; do kubectl -n istio-system port-forward deploy/prometheus 9090:9090; done

# Loki 접근
while true; do kubectl -n istio-system port-forward svc/loki 8080:80; done

# ControlZ 접근
  # Open ControlZ web UI for the istiod-123-456.istio-system pod
  istioctl dashboard controlz istiod-123-456.istio-system

  # Open ControlZ web UI for the istiod-56dd66799-jfdvs pod in a custom namespace
  istioctl dashboard controlz istiod-123-456 -n custom-ns

  # Open ControlZ web UI for any Istiod pod
  istioctl dashboard controlz deployment/istiod.istio-system

# Envoy Admin 페이지 접근
  # Details
  kubectl port-forward details-v1-65cfcf56f9-8p4gc 15001:15000 -n default
  # Ratings  
  kubectl port-forward ratings-v1-7c9bd4b87f-84q2q 15002:15000 -n default
  # Reviews v1
  kubectl port-forward reviews-v1-6584ddcf65-kljfz 15003:15000 -n default
  # Reviews v2
  kubectl port-forward reviews-v2-6f85cb9b7c-lv5hp 15004:15000 -n default
  # Reviews v3
  kubectl port-forward reviews-v3-6f5b775685-8ttfd 15005:15000 -n default

```

## 6. 정리 및 삭제

### 6.1 Bookinfo 삭제
```bash
kubectl delete -f samples/bookinfo/networking/bookinfo-gateway.yaml
kubectl delete -f samples/bookinfo/platform/kube/bookinfo.yaml
samples/bookinfo/platform/kube/cleanup.sh
```

### 6.2 Minikube 클러스터 삭제
```bash
# 특정 프로필 삭제
minikube delete -p bookinfo

# 모든 클러스터 삭제
minikube delete --all --purge
```

---

## 부가 도구 및 유틸리티 (선택사항)

### Kubeshark (네트워크 트래픽 분석)
```bash
# Kubeshark 설치
helm repo add kubeshark https://helm.kubeshark.co  
helm install kubeshark kubeshark/kubeshark  
kubectl port-forward service/kubeshark-front 8899:80 

# Kubeshark 제거
helm uninstall kubeshark
```

### WRK (부하 테스트)
```bash
# WRK 설치
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev git zlib1g-dev
git clone https://github.com/giltene/wrk2.git
cd wrk2
make
sudo cp wrk /usr/local/bin

# 트래픽 발생
wrk -t4 -c50 -d1h -R100 --latency http://192.168.49.2:31909/productpage
```

### Tetragon (보안 모니터링)
```bash
# Kind 클러스터 설정
cat <<EOF > kind-config.yaml
apiVersion: kind.x-k8s.io/v1alpha4
kind: Cluster
nodes:
  - role: control-plane
    extraMounts:
      - hostPath: /proc
        containerPath: /procHost
EOF
kind create cluster --config kind-config.yaml

# Tetragon 배포
helm repo add cilium https://helm.cilium.io
helm repo update
helm install tetragon cilium/tetragon -n kube-system
kubectl rollout status -n kube-system ds/tetragon -w
```

### 문제 해결

#### Minikube 문제 해결
```bash
# Minikube 재시작
minikube -p new start

# Docker 환경 초기화
eval $(minikube docker-env -u)

# 완전 삭제 후 재생성
minikube delete --all --purge
minikube start --driver=docker
```

#### 파일 권한 문제
```bash
# Ubuntu 파일 권한 추가
sudo chown -R $USER enable-session-resumption2.yaml
```

#### 포트 충돌 해결
```bash
# 사용중인 포트 조회
sudo lsof -i :16686
# 프로세스 종료
kill -9 PID
```

#### 시스템 제한 해결
```bash
# max_user_watches 확인
cat /proc/sys/fs/inotify/max_user_watches
cat /proc/sys/fs/inotify/max_user_instances

# 제한 상향 조정
sudo sysctl fs.inotify.max_user_instances=1024
sudo sysctl -p
```

### 재시작 시 주의사항
- 재시작 시 앱 재배포 및 gateway 재설정 필요
- 환경변수 PATH 설정 필요
- 사이드카 프록시 주입 확인 필요
