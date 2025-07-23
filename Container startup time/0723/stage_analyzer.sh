# 서비스 시작 시간을 ms단위로 측정하고
# 각 시점이 어떤 상태인지를 확인 가능함

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: $0 <service_name>"
    echo "Example: $0 productpage"
    exit 1
fi

echo "=== Detailed Container Startup Stage Analysis ==="
echo "Service: $SERVICE_NAME"
echo "Environment: Minikube 'istio' with Istio Bookinfo"

# 이벤트 모니터링 시작 (백그라운드로 실행)
kubectl get events --watch &
EVENTS_PID=$!

# 현재 시간 기록
START_TIME=$(date +%s%3N)
echo "Analysis start time: ${START_TIME}ms"

# 파드 삭제
echo ""
echo "1. Deleting existing pods..."
kubectl delete pods -l app=$SERVICE_NAME

# 파드 생성 추적
echo ""
echo "2. Tracking pod creation stages..."

# 파드가 생성될 때까지 대기
sleep 2

# 새 파드 이름 획득
POD_NAME=$(kubectl get pods -l app=$SERVICE_NAME -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$POD_NAME" ]; then
    echo "Tracking pod: $POD_NAME"
    
    # 상세 단계별 추적
    echo ""
    echo "3. Container state transitions:"
    
    for i in {1..60}; do
        CURRENT_TIME=$(date +%s%3N)
        ELAPSED=$((CURRENT_TIME - START_TIME))
        
        # 파드 상태 확인
        POD_STATUS=$(kubectl get pod $POD_NAME -o jsonpath='{.status.phase}' 2>/dev/null)
        CONTAINER_STATES=$(kubectl get pod $POD_NAME -o jsonpath='{.status.containerStatuses[*].state}' 2>/dev/null)
        READY_STATUS=$(kubectl get pod $POD_NAME -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null)
        
        echo "[${ELAPSED}ms] Pod: $POD_STATUS, Containers: $READY_STATUS"
        
        # Ready 상태 확인
        if [[ "$READY_STATUS" == *"true true"* ]]; then
            echo ""
            echo "4. Pod ready at ${ELAPSED}ms!"
            break
        fi
        
        sleep 1
    done
    
    # 최종 상세 분석
    echo ""
    echo "5. Final container analysis:"
    kubectl describe pod $POD_NAME | grep -A 20 "Containers:"
    
    echo ""
    echo "6. Recent events:"
    kubectl describe pod $POD_NAME | grep -A 10 "Events:"
    
else
    echo "Failed to find new pod for $SERVICE_NAME"
fi

# 이벤트 모니터링 완료 및 중지
kill $EVENTS_PID 2>/dev/null

echo "=== Analysis Complete ==="
