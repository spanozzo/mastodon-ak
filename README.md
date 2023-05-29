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
9. (forse non serve) abilitare tunnel minikube:
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
1. Crea un account: tootctl accounts create [username] --email [email] --confirmed 

tootctl accounts create user0 --email=user0@mail.com --confirmed 
-> psw: 61e471328b2a25f480b0074e63662565
tootctl accounts create user1 --email=user1@mail.com --confirmed 
-> psw: 1128ffe93ce179293663d43090d1239f
tootctl accounts create user2 --email=user2@mail.com --confirmed 
-> psw: 79f633eb08020107b82053171df64464
tootctl accounts create user3 --email=user3@mail.com --confirmed 
-> psw: 693d91ffe8422fce915b52daea262d80
tootctl accounts create user4 --email=user4@mail.com --confirmed 
-> psw: 853ff2bc42e8bc450604cf0adf884a0e
tootctl accounts create user5 --email=user5@mail.com --confirmed 
-> psw: 21720ae31676ce329854bcbe1d83fd79
tootctl accounts create user6 --email=user6@mail.com --confirmed 
-> psw: 644203d5ca86e14414d4e8ee309d7b79
tootctl accounts create user7 --email=user7@mail.com --confirmed 
-> psw: 9daa8a0b6bf6217caca930c39024e6db
tootctl accounts create user8 --email=user8@mail.com --confirmed 
-> psw: dc743c940dba49cb1c361725ed05a132
tootctl accounts create user9 --email=user9@mail.com --confirmed 
-> psw: 465925838f2207a2c882bde0e66e9d88


Postman flow auth (https://docs.joinmastodon.org/client/authorized/):
1. Create app: richiesta di client_id e client_secret
2. Authorize user: richiesta del codice per pubblicare 'a nome di' (fatto manualmente nel browser dopo aver effettuato il login all'istanza) [mastodon-postman panuci Authorization Code: Hwo9J7KdLhWHBvLyZHfchfZfqiIMomvk0iXHUkJf-uk]
3. Auth token: richiesta del token inserendo i 3 risultati delle precedenti query (fatto già nello script locust)