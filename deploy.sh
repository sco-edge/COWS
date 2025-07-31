#!/bin/bash

# Extended Bookinfo 배포 스크립트
# 이 스크립트는 전체 애플리케이션을 Kubernetes 클러스터에 배포합니다.

echo "🚀 Extended Bookinfo 배포를 시작합니다..."

# 1. 네임스페이스 생성
# extended-bookinfo 네임스페이스를 생성하여 모든 리소스를 격리합니다.
echo "📦 네임스페이스 생성 중..."
kubectl create namespace extended-bookinfo

# 2. Istio 자동 주입 활성화
# Istio 사이드카가 자동으로 주입되도록 네임스페이스에 라벨을 추가합니다.
# 이를 통해 서비스 메시 기능(트래픽 관리, 보안, 관찰성)을 사용할 수 있습니다.
echo "🔧 Istio 자동 주입 활성화..."
kubectl label namespace extended-bookinfo istio-injection=enabled

# 3. 기본 Bookinfo 애플리케이션 배포
# Istio의 기본 Bookinfo 샘플 애플리케이션을 배포합니다.
# 이는 productpage, details, reviews, ratings 서비스를 포함합니다.
echo "📚 기본 Bookinfo 배포 중..."
kubectl apply -f ../bookinfo.yaml

# 4. 확장된 마이크로서비스들 배포
# 10개의 추가 Python 마이크로서비스를 배포합니다.
# k8s-manifests.yaml에는 모든 서비스의 Deployment와 Service 정의가 포함되어 있습니다.
echo "🔧 확장 서비스들 배포 중..."
kubectl apply -f k8s-manifests.yaml

# 5. NodePort 서비스 배포
# 외부에서 접근할 수 있도록 NodePort 타입의 서비스를 배포합니다.
# 각 서비스는 고유한 NodePort를 가지며, 브라우저에서 직접 접근 가능합니다.
echo "🌐 NodePort 서비스 배포 중..."
kubectl apply -f nodeport-services.yaml

# 6. 배포 상태 확인
echo "✅ 배포 완료! 상태를 확인합니다..."
echo "📊 파드 상태:"
kubectl get pods -n extended-bookinfo

echo "🌐 서비스 상태:"
kubectl get services -n extended-bookinfo

echo "🎉 배포가 완료되었습니다!"
echo "📱 포털 접근: http://$(minikube ip -p istiotest):30081"
echo "👥 사용자 서비스: http://$(minikube ip -p istiotest):30082"
echo "📦 주문 서비스: http://$(minikube ip -p istiotest):30085"
echo "📚 카탈로그 서비스: http://$(minikube ip -p istiotest):30083" 