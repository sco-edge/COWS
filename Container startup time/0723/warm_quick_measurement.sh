# pod삭제 후 재설치는 warm start 이므로, deployment/replicaset을 제거한 후
# pod를 재배포해야 cold start time을 측정가능함(수정예정)

echo "=== Bookinfo Cold Start Quick Measurement ==="
echo "Environment: Minikube 'istio' profile with Istio Bookinfo"

# 현재 환경 확인
echo "Checking current Bookinfo pods..."
kubectl get pods | grep -E "(productpage|details|reviews|ratings)"

echo ""
echo "Starting measurement..."

# 각 서비스별로 순차적으로 재시작하며 시간 측정
services=("productpage" "details" "reviews" "ratings")

for service in "${services[@]}"; do
    echo ""
    echo "=== Measuring $service cold start ==="
    
    # 시작 시간 기록
    start_time=$(date +%s%3N)
    
    # 파드 삭제
    kubectl delete pods -l app=$service
    
    # 파드 재생성 대기
    kubectl wait --for=condition=ready pod -l app=$service --timeout=300s
    
    # 완료 시간 기록
    end_time=$(date +%s%3N)
    
    # 시간 계산
    duration=$((end_time - start_time))
    
    echo "$service cold start time: ${duration}ms"
    
    # 컨테이너 수 확인 (Istio sidecar 포함)
    containers=$(kubectl get pods -l app=$service -o jsonpath='{.items[0].spec.containers[*].name}')
    container_count=$(echo $containers | wc -w)
    
    echo "$service containers: $containers"
    echo "$service container count: $container_count"
    
    sleep 5
done

echo ""
echo "=== Measurement Complete ==="
echo "End"
