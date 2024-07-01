## 그라파나 실행
kubectl port-forward svc/grafana 3000:3000 -n istio-system
kubectl -n istio-system port-forward deploy/grafana 3000:3000
kubectl -n istio-system port-forward svc/grafana 3000:80

## 프로메테우스 실행
kubectl port-forward svc/prometheus 9090:9090 -n istio-system
kubectl -n istio-system port-forward deploy/prometheus 9090:9090
kubectl -n istio-system port-forward svc/prometheus-server 9090:80

## 현재 사용중인 마이크로 서비스 확인(서비스 메시가 설치된 네임스페이스를 확인)
$ kubectl get namespaces
NAME              STATUS   AGE
default           Active   8d
istio-bookinfo    Active   2d6h
istio-system      Active   2d6h
kube-node-lease   Active   8d
kube-public       Active   8d
kube-system       Active   8d

## ISTIO 구성요소 확인(istio-bookinfo)
$ kubectl get pods -n istio-bookinfo
NAME                              READY   STATUS    RESTARTS      AGE
details-v1-6c98bc7c4c-j6xw9       1/1     Running   1 (95m ago)   2d6h
productpage-v1-6d56b97dfb-qmcx4   1/1     Running   2 (95m ago)   2d6h
ratings-v1-7645575cf9-2t9ln       1/1     Running   1 (95m ago)   2d6h
reviews-v1-6c5c97576c-8wmbj       1/1     Running   1 (95m ago)   2d6h
reviews-v2-575d87db6c-6gtwt       1/1     Running   1 (95m ago)   2d6h
reviews-v3-698c4b8d4c-rsbq7       1/1     Running   1 (95m ago)   2d6h

## Kiali 대시보드 사용 - Kiali를 통해 서비스 메쉬를 시각적으로 확인할 수 있습니다.
kubectl get pods -n istio-system | grep kiali
kubectl port-forward -n istio-system svc/kiali 20001:20001

## mTLS 적용 여부 확인
$ kubectl get peerauthentication -A
NAMESPACE      NAME           MODE      AGE
istio-system   disable-mtls   DISABLE   55s

## minikube 강제 시작
minikube status
minikube stop
minikube delete
minikube start --force --wait=all
