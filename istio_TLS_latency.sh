### 마이크로서비스 간 TLS로 인한 평균 지연 시간
sum(rate(istio_request_duration_milliseconds_sum{security_istio_io_tlsMode="istio"}[1m])) 
/ 
sum(rate(istio_request_duration_milliseconds_count{security_istio_io_tlsMode="istio"}[1m]))

### TLS 껐을 때의 평균 지연 시간
sum(rate(istio_request_duration_milliseconds_sum{security_istio_io_tlsMode!="istio"}[1m])) 
/ 
sum(rate(istio_request_duration_milliseconds_count{security_istio_io_tlsMode!="istio"}[1m]))

### TLS 켜고 껐을 때의 지연 시간 비교
(
  sum(rate(istio_request_duration_milliseconds_sum{security_istio_io_tlsMode="istio"}[1m])) 
  / 
  sum(rate(istio_request_duration_milliseconds_count{security_istio_io_tlsMode="istio"}[1m]))
) 
- 
(
  sum(rate(istio_request_duration_milliseconds_sum{security_istio_io_tlsMode!="istio"}[1m])) 
  / 
  sum(rate(istio_request_duration_milliseconds_count{security_istio_io_tlsMode!="istio"}[1m]))
)

### 특정 서비스 별 TLS 지연 시간 측정 (e.g., productpage)
sum(rate(istio_request_duration_milliseconds_sum{security_istio_io_tlsMode="istio", destination_service_name="productpage"}[1m])) 
/ 
sum(rate(istio_request_duration_milliseconds_count{security_istio_io_tlsMode="istio", destination_service_name="productpage"}[1m]))

### TLS 지연 측정 시간 히스토그램 출력
histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket{security_istio_io_tlsMode="istio"}[1m])) by (le))

### 히스토그램 버킷별 모든 데이터 출
sum(rate(istio_request_duration_milliseconds_bucket{security_istio_io_tlsMode="istio"}[1m])) by (le)

