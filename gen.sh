# Generate CA's private key and self-signed certificate
openssl req -x509 -newkey rsa:4096 -days 365 -keyout ca-key.pem -out ca-cert.pem

openssl x509 -in ca-cert.pem -noout -text
# Generate web server's private key and certificate signing request (CSR)

# Use CA's private key to sign web server's CSR and get back the signed certificate