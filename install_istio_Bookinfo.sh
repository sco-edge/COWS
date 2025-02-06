### 재부팅시
minikube -p new start
환경변수 설정(export PATH="$PATH:/home/junho/Documents/istio-1.23.0/bin")



### minikube 신규 생성
minikube start -p hellworld # helloworld 라는 이름의 profile로 생성

### minikube 리스트
minikube profile list

### minikube 프로파일 new로 변경
minikube profile new

### 현재 사용중인 profile 조회
minikube profile

### K8s deployment 시간 변경
kubectl set env deployment/디플로이 이름 TZ="Asia/Seoul"

## minikube 용량 부족
### max_user_watches 확인
cat /proc/sys/fs/inotify/max_user_watches
### max_user_instances 확인
cat /proc/sys/fs/inotify/max_user_instances

### 제한 instance 수 상향
sudo sysctl fs.inotify.max_user_instances=1024
sudo sysctl -p
### 영구 적용 시
### /etc/sysctl.conf에서 fs.inotify.max_user_instances을 수정

### bookinfo이름을 가진 minikube 생성
minikube start -p bookinfo --memory 8192 --cpus 4

### new 이름을 가진 minikube 재시작
minikube -p new start

### kubeshark 포트포워딩
kubectl port-forward svc/kubeshark-front 8899:80 -n default
### k8s dashboard 포트포워딩(수정 필요)
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8446:443


### Docker 설치
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64

### Docker 미작동(virtual box 설치로 해결)
sudo apt install virtualbox

### 부팅시 Docker 자동 실행
sudo systemctl enable docker

### 잔여 클러스터 제거(CRDs 설치 불가시 적용, 이후 istio 재설치 필요)
istioctl x uninstall --purge
kubectl delete namespace istio-system
혹은
kubectl kustomize "github.com/kubernetes-sigs/gateway-api/config/crd?ref=v0.8.0" | kubectl apply -f -


### istio 설치
curl -L https://istio.io/downloadIstio | sh -

### 1.6 버전 지정 설치
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.6.8 TARGET_ARCH=x86_64 sh -

cd istio-<version>
export PATH=$PWD/bin:$PATH
export PATH="$PATH:/home/junho/Documents/istio-1.23.0/bin"
### export PATH="$PATH:/home/junho/Documents/istio-1.6.8/bin"
### export PATH="$PATH:/home/junho/Documents/istio-1.8.3/bin"

### CRD 문제
istioctl install --set profile=demo -y

### istio 설치 파일 적용
istioctl install --set profile=demo -y

### Istio 시스템 네임스페이스와 기본 네임스페이스에 레이블 추가
kubectl label namespace default istio-injection=enabled
cd Documents/istio-1.22.3/

### Bookinfo 애플리케이션 배포
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml

cd samples/bookinfo
### 애플리케이션 인그레스 게이트웨이 설정
kubectl apply -f networking/bookinfo-gateway.yaml

### k8s에서 pod의 제거가 되지 않을 때(replica set을 삭제해야 함)
### replica set 제거
kubectl delete replicaset {레플리카셋 이름}
### 레플리카셋 정보 조회
kubectl get replicasets
### 레플리카셋 상세 정보 조회
kubectl describe replicasets
### YAML 형식으로 조회하기
kubectl get respliasets {레플리카셋 이름} -o=yaml

### 게이트웨이의 IP 주소/포트 확인
******** 
kubectl get svc istio-ingressgateway -n istio-system

### jaeger, loki, grafana, kiali, prometheus 일괄 설치
cd samples/addons
kubectl apply -f jaeger.yaml
kubectl apply -f loki.yaml
kubectl apply -f grafana.yaml
kubectl apply -f kiali.yaml
kubectl apply -f prometheus.yaml

cd extras
kubectl apply -f zipkin.yaml
kubectl apply -f skywalking.yaml

### 정상 배포 확인
kubectl get services
kubectl get pods

### 사이드카 프록시 주입
kubectl label namespace default istio-injection=enabled
kubectl label namespace istio-system istio-injection=enabled
### 주입 후에도 kiali에서 인식이 안될 시 파드 제거 후 재배포/minikube 재시작 때도 필요
kubectl delete -f ~/Documents/istio-1.23.0/samples/bookinfo/platform/kube/bookinfo.yaml
kubectl apply -f ~/Documents/istio-1.23.0/samples/bookinfo/platform/kube/bookinfo.yaml

*** tracing이 정상적으로 되지 않을 때: 
https://istio.io/latest/docs/tasks/observability/distributed-tracing/sampling/

*** minikube 재부팅시 추적 활성화하는 법
kubectl delete namespace observability
kubectl create namespace observability

### observerability 사이드카 주입
kubectl label namespace observability istio-injection=enabled

kubectl delete -f samples/open-telemetry/otel.yaml -n observability
kubectl apply -f samples/open-telemetry/otel.yaml -n observability

### ubuntu 파일 권한 추가
sudo chown -R junho enable-session-resumption2.yaml
chown -R $username

### 사용중인 포트 조회 및 포트 죽이기
sudo lsof -i :16686 // 16686 포트를 사용중인 프로세스 조회
kill -9 PID // PID 프로세스 삭제

### kubeshark 설치
helm repo add kubeshark https://helm.kubeshark.co  
helm install kubeshark kubeshark/kubeshark  
kubectl port-forward service/kubeshark-front 8899:80 

### kubeshark 제거
helm uninstall kubeshark

***
cat <<EOF | istioctl install -y -f -
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    enableTracing: true
    defaultConfig:
      tracing:
        sampling: 10
    extensionProviders:
    - name: otel-tracing
      opentelemetry:
        port: 4317
        service: opentelemetry-collector.observability.svc.cluster.local
        resource_detectors:
          environment: {}
EOF

***
kubectl delete -f - <<EOF
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: otel-tracing
EOF

***
kubectl apply -f - <<EOF
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: otel-tracing
EOF

***
cat <<EOF | istioctl delete -y -f -
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    enableTracing: true
    extensionProviders:
    - name: otel-tracing
      opentelemetry:
        port: 4317
        service: opentelemetry-collector.observability.svc.cluster.local
        resource_detectors:
          environment: {}
EOF

***
cat <<EOF | istioctl install -y -f -
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    enableTracing: true
    extensionProviders:
    - name: otel-tracing
      opentelemetry:
        port: 4317
        service: opentelemetry-collector.observability.svc.cluster.local
        resource_detectors:
          environment: {}
EOF

***
kubectl delete -f - <<EOF
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
   name: otel-demo
spec:
  tracing:
  - providers:
    - name: otel-tracing
    randomSamplingPercentage: 10
EOF

***
kubectl apply -f - <<EOF
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
   name: otel-demo
spec:
  tracing:
  - providers:
    - name: otel-tracing
    randomSamplingPercentage: 10
EOF

=========<맨 위부터 이곳까지 드래그하여 복붙 시 one-click install 가능>=========

## minikube apiserver:stopped => 1st method
sudo apt-get purge -y docker-engine docker docker.io docker-ce docker-ce-cli
sudo apt-get autoremove -y --purge docker-engine docker docker.io docker-ce
sudo rm -rf /var/lib/docker /etc/docker
sudo rm /etc/apparmor.d/docker
sudo groupdel docker
sudo rm -rf /var/run/docker.sock

## minikube apiserver:stopped => 2nd method
eval $(minikube docker-env -u)

## 모니터링 툴 Prometheus 접근
while true; do kubectl -n istio-system port-forward deploy/prometheus 9090:9090; done

## Grafana 접근
while true; do kubectl -n istio-system port-forward deploy/grafana 3000:3000; done

## Loki 접근
while true; do kubectl -n istio-system port-forward svc/loki 8080:80; done

# Checkout the source code
mkdir kiali_sources
cd kiali_sources
export KIALI_SOURCES=$(pwd)

git clone https://github.com/kiali/kiali.git
git clone https://github.com/kiali/kiali-operator.git
git clone https://github.com/kiali/helm-charts.git

ln -s $KIALI_SOURCES/kiali-operator kiali/operator

# Build the back-end and run the tests
cd $KIALI_SOURCES/kiali
make build test

# You can pass go test flags through the GO_TEST_FLAGS env var
# make -e GO_TEST_FLAGS="-race -v -run=\"TestCanConnectToIstiodReachable\"" test

# Build the front-end and run the tests
make build-ui-test

cd $KIALI_SOURCES/kiali
make kiali-reload-image

## Kiali 접근
istioctl dashboard kiali

### Jaeger 대시보드
istioctl dashboard jaeger
kubectl -n istio-system port-forward deploy/jaeger 16686:16686
### trace 추적
kubectl -n istio-system port-forward svc/jaeger-query 16685:16686 -n istio-system

## Zipkin 접근
kubectl -n istio-system port-forward svc/zipkin 9411:9411

### Zipkin 설명
Zipkin 은 분산 추적 시스템입니다. 서비스 아키텍처에서 지연 문제를 해결하는 데 필요한 타이밍 데이터를 수집하는 데 도움이 됩니다. 이 데이터의 수집과 조회가 모두 특징입니다.

Zipkin은 Jaeger의 대안이며 기본적으로 배포되지 않습니다. Jaeger를 Zipkin으로 바꾸려면 를 실행합니다. 또한 사용되지 않을 Jaeger 배포를 로 제거 하거나 시작하기kubectl delete deployment jaeger 의 선택적 설치 단계에 따라 처음부터 설치하지 않을 수도 있습니다 .

### Zipkin 설치
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

### Zipkin 연동
https://docs.traceable.ai/docs/istio-with-zipkin

### Zipkin 실행
minikube service zipkin -n default

### helm 저장소 추가
helm repo add openzipkin https://openzipkin.github.io/zipkin-chart/
helm repo update

### label 확인 명령어
kubectl get ns istio-system --show-labels

### istio-system의 구성 파드들 나열
kubectl get pods -n istio-system

### 트래픽 라우팅 설정
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml

### wrk 설치
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev git zlib1g-dev
sudo git clone https://github.com/giltene/wrk2.git
cd wrk2
sudo make
# move the executable to somewhere in your PATH
sudo cp wrk /usr/local/bin

### wrk2 설치
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev git zlib1g-dev
git clone https://github.com/giltene/wrk2.git
cd wrk2
make
# move the executable to somewhere in your PATH
sudo cp wrk /usr/local/bin

### 트래픽 발생
wrk -t4 -c50 -d1h -R100 --latency http://192.168.49.2:31909/productpage
wrk -t2 -c50 -d1h -R100 --latency http://192.168.49.2:31307/productpage

### wrk debug
wrk -t2 -c50 -d1h -R100 --latency http://192.168.49.2:31307/productpage -- debug true

### CRD 문제
istioctl install --set profile=demo -y

### 기존에 존재하던 쿠버네티스 컨테이너 혹은 도커 컨테이너 조회
kubectl config get-contexts

### 필요없는 컨텍스트 삭제
kubectl config delete-context <context-name>

### 쿠버네티스 충돌 및 미니쿠베 제거
minikube delete --all --purge

### 충돌시 도커 컨테이너 및 이미지 제거

### pod가 위치한 namespace 검색(e.g., media-frontend가 속한 namespace 검색
kubectl get pods --all-namespaces -l io.kompose.service=media-frontend

--------------------------------
### bookinfo 설치
curl -L https://istio.io/downloadIstio | sh -
cd istio-<version>
export PATH=$PWD/bin:$PATH
export PATH="$PATH:/home/junho/Documents/istio-1.22.3/bin"

istioctl install --set profile=demo -y

kubectl label namespace default istio-injection=enabled

kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml

kubectl get services
kubectl get pods

kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml

kubectl get svc istio-ingressgateway -n istio-system

### DSB socialNetwork(media-fronted) 웹페이지 접속(default namespace안에 존재함)
kubectl get svc media-frontend -n default

### bookinfo 제거
kubectl ctx -d istio
kubectl config delete-cluster istio
kubectl config delete-user istio
-------------------------------------
### minikube 클러스터 완전히 삭제하기
sudo apt-get purge kubeadm kubectl kubelet kubernetes-cni kube*   
sudo apt-get autoremove  
sudo rm -rf ~/.kube

kubectl delete -f https://raw.githubusercontent.com/istio/istio/release-1.23/samples/bookinfo/platform/kube/bookinfo.yaml
kubectl delete -f https://raw.githubusercontent.com/istio/istio/release-1.23/samples/bookinfo/networking/bookinfo-gateway.yaml


### docker 자동으로 시작하게 만들기
sudo systemctl enable docker

### minikube start가 안될 떄
minikube delete
minikube start --driver=docker

GUI Enable
$ sudo systemctl set-default graphical
GUI Disable
$ sudo systemctl set-default multi-user

### minikube 실행 안됨
minikube delete --all --purge

### Use krew
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

## Tetragon
### 설치
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
EXTRA_HELM_FLAGS=(--set tetragon.hostProcPath=/procHost) # flags for helm install

### deploy Tetragon
helm repo add cilium https://helm.cilium.io
helm repo update
helm install tetragon ${EXTRA_HELM_FLAGS[@]} cilium/tetragon -n kube-system
kubectl rollout status -n kube-system ds/tetragon -w

### deploy demo app
kubectl create -f https://raw.githubusercontent.com/cilium/cilium/v1.15.3/examples/minikube/http-sw-app.yaml

### 모두 정리 cleanup.sh
samples/bookinfo/platform/kube/cleanup.sh
=> 재시작 시 앱 재배포 및 gateway 재설정 필요
