## 그라파나 실행
kubectl port-forward svc/grafana 3000:3000 -n istio-system
kubectl -n istio-system port-forward deploy/grafana 3000:3000
kubectl -n istio-system port-forward svc/grafana 3000:80

## 프로메테우스 실행
kubectl port-forward svc/prometheus 9090:9090 -n istio-system
kubectl -n istio-system port-forward deploy/prometheus 9090:9090
kubectl -n istio-system port-forward svc/prometheus-server 9090:80