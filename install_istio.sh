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

