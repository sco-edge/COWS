### 마이크로서비스 간 TLS로 인한 평균 지연 시간

sum(rate(istio_request_duration_milliseconds_sum{security_istio_io_tlsMode="istio"}[1m])) 
/ 
sum(rate(istio_request_duration_milliseconds_count{security_istio_io_tlsMode="istio"}[1m]))
