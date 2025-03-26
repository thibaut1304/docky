# README

## Préparation setup ssh

- Sur la machine avec l'API :   
	- **Creation clef ssh** :  
	`ssh-keygen -t rsa -b 4096 -f ~/.ssh/api-docker -N ""`

- Sur la machine ou on veux ecouter les container docker (cible) :  
	- `sudo adduser --disabled-password --gecos "" api-docker`
	- `sudo mkdir -p /home/api-docker/.ssh`
	- `sudo vim /home/api-docker/.ssh/authorized_keys`
	- `sudo chown -R api-docker:api-docker /home/api-docker/.ssh`
	- `sudo chmod 700 /home/api-docker/.ssh`
	- `sudo chmod 600 /home/api-docker/.ssh/authorized_keys`
	- `sudo usermod -aG docker api-docker`

- Sur la machine avec l'API : Tester la connection ssh avec la clef crée !  
Si non fonctionnelle ne pas aller plus loin et vérifier la configuration de votre machine distante `/etc/ssh/sshd_config`       
	- `ssh -i ~/.ssh/api-docker api-docker@192.168.x.x`


## Creer et remplir le fichier de configuration config.json comme l'example.

- type == local ou ssh
- Un test ssh sera effectué sur la machine voir logs avec `docker-compose logs`

## Creer et remplir le docker-compose.yml voir exemple
- Faites un copier coller et ne modifier que le port ou le fuseaux horaire ou le volume sur votre clef ssh crée sur les premères étapes

## Creer un fichier .env a la racine du projet
- Le minimum possible dans de fichier sont :
	- API_VERSION=0.1.3		# Le service homer ecoute sur l'endpoint v0 donc si non présente l'endpoint sera v1
	- DOCKY_TOEN=votre_token_secret 

# Lancement du projet
Une fois ces fichier crée lancez le projet simplement avec la commande : `./run.sh`
<!-- 
# TODO:
Probleme ssh agent avec 2 worker unicorn 
-->
