# https://dev.to/techschoolguru/how-to-create-sign-ssl-tls-certificates-2aai
rm *.pem

# Generate CA's private key and self-signed certificate
openssl req -x509 -newkey rsa:4096 -days 365 -keyout ca-key.pem -out ca-cert.pem -subj "C = ko/ST = Seoul/L = Seoul/O = korea/OU = KU/CN = bjhbae@korea.ac.kr/emailAddress = bjhbae@korea.ac.kr"

echo "CA's self-signed certificate"
openssl x509 -in ca-cert.pem -noout -text
# Generate web server's private key and certificate signing request (CSR)
openssl req -newkey rsa:4096 -keyout server-key.pem -out server-req.pem -subj "C = ko/ST = Seoul/L = Seoul/O = korea/OU = KU/CN = bjhbae@korea.ac.kr/emailAddress = bjhbae@korea.ac.kr"
# Use CA's private key to sign web server's CSR and get back the signed certificate
openssl x509 -req -in server-req.pem -days 60 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -extfile servcer-ext.cnf

echo "Server's signed certificate"
openssl x509 -in server-cert.pem -noout -text