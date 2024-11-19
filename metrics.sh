### istio metrics

### 서비스에 대한 총 요청 수(productpage)
istio_requests_total{destination_service="productpage.default.svc.cluster.local"}

### v3 서비스에 대한 모든 요청의 총 수(reviews)
istio_requests_total{destination_service="reviews.default.svc.cluster.local", destination_version="v3"}

### 5분동안 서비스의 모든 인스턴스에 대한 요청 비율(productpage)
rate(istio_requests_total{destination_service=~"productpage.*",response_code="200"}[5m])
