### istio metrics

### 5분동안 서비스의 모든 인스턴스에 대한 요청 비율(productpage)
rate(istio_requests_total{destination_service=~"productpage.*",response_code="200"}[5m])
