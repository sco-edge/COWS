#!/bin/bash

# Docker 이미지 빌드 스크립트
# 이 스크립트는 모든 마이크로서비스의 Docker 이미지를 빌드합니다.

echo "🐳 Docker 이미지 빌드를 시작합니다..."

# Minikube Docker 환경 설정
# Minikube는 자체 Docker 데몬을 사용하므로, 이를 사용하도록 환경을 설정해야 합니다.
# 이렇게 하면 빌드된 이미지가 Minikube 클러스터에서 사용할 수 있습니다.
echo "🔧 Minikube Docker 환경 설정 중..."
eval $(minikube docker-env -p istiotest)

# Docker 빌드 함수
# 각 서비스의 Docker 이미지를 빌드하는 함수입니다.
build_service() {
    local service_name=$1
    local service_path=$2
    
    echo "🔨 $service_name 이미지 빌드 중..."
    
    # Docker 빌드 명령어
    # -t: 이미지 태그 지정
    # --no-cache: 캐시를 사용하지 않고 완전히 새로 빌드 (UI 변경 시 유용)
    docker build --no-cache -t extended-bookinfo/$service_name:latest $service_path/
    
    if [ $? -eq 0 ]; then
        echo "✅ $service_name 이미지 빌드 완료"
    else
        echo "❌ $service_name 이미지 빌드 실패"
        exit 1
    fi
}

# 각 서비스별 이미지 빌드
# 모든 마이크로서비스의 Docker 이미지를 순차적으로 빌드합니다.

echo "📚 Library Portal 빌드 중..."
build_service "library-portal" "library-portal"

echo "👥 User Service 빌드 중..."
build_service "user-service" "user-service"

echo "📦 Order Service 빌드 중..."
build_service "order-service" "order-service"

echo "📚 Catalog Service 빌드 중..."
build_service "catalog-service" "catalog-service"

echo "📦 Inventory Service 빌드 중..."
build_service "inventory-service" "inventory-service"

echo "💳 Payment Service 빌드 중..."
build_service "payment-service" "payment-service"

echo "🔔 Notification Service 빌드 중..."
build_service "notification-service" "notification-service"

echo "🔍 Search Service 빌드 중..."
build_service "search-service" "search-service"

echo "🎯 Recommendation Service 빌드 중..."
build_service "recommendation-service" "recommendation-service"

echo "📊 Analytics Service 빌드 중..."
build_service "analytics-service" "analytics-service"

echo "🚚 Shipping Service 빌드 중..."
build_service "shipping-service" "shipping-service"

# 빌드된 이미지 확인
echo "📋 빌드된 이미지 목록:"
docker images | grep extended-bookinfo

echo "🎉 모든 Docker 이미지 빌드가 완료되었습니다!"
echo ""
echo "📝 다음 단계:"
echo "  1. ./deploy.sh 실행하여 Kubernetes에 배포"
echo "  2. kubectl get pods -n extended-bookinfo 로 상태 확인"
echo "  3. http://$(minikube ip -p istiotest):30081 로 포털 접근" 