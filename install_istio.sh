### istio 설치
curl -L https://istio.io/downloadIstio | sh -
cd istio-<version>
export PATH=$PWD/bin:$PATH

### istio 설치 파일 적용
istioctl install --set profile=demo -y

### Istio 시스템 네임스페이스와 기본 네임스페이스에 레이블 추가
kubectl label namespace default istio-injection=enabled

### Bookinfo 애플리케이션 배포
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml

### 정상 배포 확인
kubectl get services
kubectl get pods

### 애플리케이션 인그레스 게이트웨이 설정
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml

### 게이트웨이의 IP 주소/포트 확인
kubectl get svc istio-ingressgateway -n istio-system

## 모니터링 툴 Prometheus 접근
kubectl -n istio-system port-forward svc/prometheus 9090:9090

## Grafana 접근
kubectl -n istio-system port-forward svc/grafana 3000:3000
