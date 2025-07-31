kubectl delete peerauthentication disable-mtls -n istio-system
### kubectl get peerauthentication -A
## 기존에 disable 되어있는 mtls를 다시 able 시키기 위해서는 대상의 name과 namespace의 이름이 일치해야 한다.

kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: disable-mtls
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
EOF


### extended-bookinfo
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: disable-mtls
  namespace: extended-bookinfo
spec:
  mtls:
    mode: STRICT
EOF
