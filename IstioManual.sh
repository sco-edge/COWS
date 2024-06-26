## 그라파나 실행
kubectl port-forward svc/grafana 3000:3000 -n istio-system
kubectl -n istio-system port-forward deploy/grafana 3000:3000
kubectl -n istio-system port-forward svc/grafana 3000:80

## 프로메테우스 실행
kubectl port-forward svc/prometheus 9090:9090 -n istio-system
kubectl -n istio-system port-forward deploy/prometheus 9090:9090
kubectl -n istio-system port-forward svc/prometheus-server 9090:80

## 현재 사용중인 마이크로 서비스 확인
$ kubectl get namespaces
NAME              STATUS   AGE
default           Active   8d
istio-bookinfo    Active   2d6h
istio-system      Active   2d6h
kube-node-lease   Active   8d
kube-public       Active   8d
kube-system       Active   8d