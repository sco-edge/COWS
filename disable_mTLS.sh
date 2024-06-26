kubectl delete peerauthentication enable-mtls-default -n default
kubectl delete peerauthentication enable-mtls-istio-system -n istio-system

kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: disable-mtls
  namespace: istio-system
spec:
  mtls:
    mode: DISABLE
EOF