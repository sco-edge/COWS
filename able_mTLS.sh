kubectl delete peerauthentication disable-mtls -n istio-system

kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: enable-mtls
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
EOF