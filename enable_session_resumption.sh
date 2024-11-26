apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: enable-session-resumption
  namespace: istio-system
spec:
  workloadSelector:
    labels:
      istio: ingressgateway  # 적용할 워크로드의 레이블
  configPatches:
  - applyTo: FILTER_CHAIN
    match:
      listener:
        portNumber: 443  # HTTPS 포트
        filterChain:
          filter:
            name: "envoy.filters.network.tls_context"
    patch:
      operation: MERGE
      value:
        common_tls_context:
          tls_session_ticket_keys: # 세션 티켓 설정
            - inline_string: "c29tZXRoaW5nc2Vzc2lvbmhleQ=="  # Base64로 인코딩된 키


### 적용
kubectl apply -f enable-session-resumption.yaml

### session resumption 적용 해제
tls_session_ticket_keys: []

