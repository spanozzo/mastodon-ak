# akamas-mastodon

Chart from: https://github.com/mastodon/chart

# Modifiche
1. Setting dei vari parametri essenziali in config_values.yaml
2. Disabilitato ElasticSearch in quanto necessita di troppe risorse per minikube e non riesce a deployare pos webapp
3. Setting dell'Ingress. Applicativo richiede connessione https (non sembra esserci la possibilità anche in ambiente di develop di disabilitare il forcing di questo)


# Deploy
1. variabili settate in config_values.yaml
2. helm dep update
3. helm install --namespace mastodon --create-namespace my-mastodon ./ -f config_values.yaml
4. Generazione chiave 'ca.key':
openssl genpkey -algorithm RSA -out ca.key -pkeyopt rsa_keygen_bits:2048
5. Generazione certificato 'ca.crt':
openssl req -x509 \
  -new -nodes  \
  -days 365 \
  -key ca.key \
  -out ca.crt \
  -subj "/CN=yourdomain.com" \
  -addext "subjectAltName = DNS:mastodon.local"	
6. Aggiunta certificato a k8s:
kubectl create secret tls mastodon-tls -n mastodon \
--key ca.key \
--cert ca.crt
(opzionali minikube):
7. Abilitare ingress minikube:
minikube addons enable ingress
8. set'[minikube ip] mastodon.local' in /etc/hosts
9. abilitare tunnel minikube:
minikube tunnel

(se windows):
1. settato '127.0.0.1 mastodon.local' C:\Windows\System32\drivers\etc\hosts
2. settato '[minikube ip] mastodon.local' in /etc/hosts in wsl
3. 'minikube tunnel'
-> accessibile da Windows

Query postgresql:
1. apri shell nel container: kubectl -n mastodon exec -it my-mastodon-postgresql-0 -- bash
2. connettiti a postgresql: psql -U mastodon mastodon_production              (psw: admin)
3. lista delle table: \dt

Command line: https://docs.joinmastodon.org/admin/tootctl/
1. Crea un account: tootctl accounts create [username] --email [email] --confirmed --role [role]


Postman flow auth (https://docs.joinmastodon.org/client/authorized/):
1. Create app: richiesta di client_id e client_secret
2. Authorize user: richiesta del codice per pubblicare 'a nome di' (fatto manualmente nel browser dopo aver effettuato il login all'istanza) [mastodon-postman panuci Authorization Code: Hwo9J7KdLhWHBvLyZHfchfZfqiIMomvk0iXHUkJf-uk]
3. Auth token: richiesta del token inserendo i 3 risultati delle precedenti query