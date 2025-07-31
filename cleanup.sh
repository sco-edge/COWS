#!/bin/bash

# Extended Bookinfo 정리 스크립트
# 이 스크립트는 배포된 모든 리소스를 정리합니다.

echo "🧹 Extended Bookinfo 정리를 시작합니다..."

# 1. 네임스페이스 삭제
# extended-bookinfo 네임스페이스를 삭제하면 해당 네임스페이스의 모든 리소스가 함께 삭제됩니다.
# 이는 Deployment, Service, Pod, ConfigMap, Secret 등 모든 Kubernetes 리소스를 포함합니다.
echo "🗑️ 네임스페이스 삭제 중..."
kubectl delete namespace extended-bookinfo

# 2. 기본 Bookinfo 애플리케이션 삭제
# Istio의 기본 Bookinfo 샘플 애플리케이션을 삭제합니다.
# 이는 productpage, details, reviews, ratings 서비스를 포함합니다.
echo "📚 기본 Bookinfo 삭제 중..."
kubectl delete -f ../bookinfo.yaml

# 3. NodePort 서비스 삭제
# 외부 접근을 위한 NodePort 서비스들을 삭제합니다.
echo "🌐 NodePort 서비스 삭제 중..."
kubectl delete -f nodeport-services.yaml

# 4. Docker 이미지 정리 (선택사항)
# 빌드된 Docker 이미지들을 삭제합니다. 디스크 공간을 절약할 수 있습니다.
echo "🐳 Docker 이미지 정리 중..."
docker images | grep extended-bookinfo | awk '{print $3}' | xargs -r docker rmi

# 5. 정리 완료 확인
echo "✅ 정리 완료! 상태를 확인합니다..."

# 네임스페이스가 삭제되었는지 확인
if kubectl get namespace extended-bookinfo 2>/dev/null; then
    echo "⚠️ extended-bookinfo 네임스페이스가 아직 존재합니다."
else
    echo "✅ extended-bookinfo 네임스페이스가 성공적으로 삭제되었습니다."
fi

# 기본 Bookinfo 리소스 확인
echo "📊 기본 Bookinfo 리소스 상태:"
kubectl get pods -l app=productpage 2>/dev/null || echo "✅ 기본 Bookinfo 파드가 삭제되었습니다."
kubectl get pods -l app=details 2>/dev/null || echo "✅ Details 파드가 삭제되었습니다."
kubectl get pods -l app=reviews 2>/dev/null || echo "✅ Reviews 파드가 삭제되었습니다."
kubectl get pods -l app=ratings 2>/dev/null || echo "✅ Ratings 파드가 삭제되었습니다."

echo "🎉 정리가 완료되었습니다!"
echo ""
echo "📝 정리된 리소스들:"
echo "  - extended-bookinfo 네임스페이스 및 모든 리소스"
echo "  - 기본 Bookinfo 애플리케이션"
echo "  - NodePort 서비스들"
echo "  - Docker 이미지들 (선택사항)"
echo ""
echo "🔄 다시 배포하려면:"
echo "  1. ./build-images.sh 실행"
echo "  2. ./deploy.sh 실행" 