# Changelog

## [0.1.3]
### :rocket: Nouveautés
- - **Route `/metrics/{name_conatiners}`**  
	-> Permet d'afficher les metrics d' un container specifique
	-> Informations affichées : Status, uptime, cpu_percent, memory, restartsCount
	-> possibilié de les cacher les parametres !
### :bug: Corrections
- Fix erreur certificat en mode prod
- Fix nom response status code LIST_CONTAINERS

### :fire: Notes
- Bug a fix probleme de ssh agent conenction ssh a cause de uvicorn si plusieurs worker !

## [0.1.2]
### :rocket: Nouveautés
- Gestion propre des hotes distants ssh pour facilement ajouter des entrypoint docker.sock voir fichier de config.json
- Modifications des routes containers pour afficher que ceux qui sont `running`
- **Route `/containers/name`**  
	-> Permet d'afficher la liste des noms des conteneurs Docker.
	-> Informations affichées : Nom
- **Route `/containers/{name_conatiners}`**  
	-> Permet d'afficher les informations d' un container specifique
	-> Informations affichées : ID, nom, image, ports, et statut.

### :bug: Corrections
-  

### :fire: Notes
- 


## [0.1.1] -- Première version stable
### :rocket: Nouveautés
- **Route `/containers`**  
	-> Permet d'afficher la liste des conteneurs Docker, à la fois **locaux** et **distants** via connexion SSH.  
	-> Informations affichées : ID, nom, image, ports, et statut.
- **Route `/status`**  
  → Fournit des informations sur la version actuelle de l'API Docky et son état.  
- Middlewares require_token pour sécuriser l'acces avec un token d'identifications
- Logger avec emoji et envoie sur server mqtt pour un suivis des logs a distances voir [https://thusser.com/logs](Logs Viewer)
- Reponse code et tatus centralise pour une meilleur gestion des response
- Ajout d'un limiter de facon global
- Ajout d'handler pour erreur 404, 500 et 429
- Ajout du server dans le schema d'openapi

### :bug: Corrections
-  

### :fire: Notes
- 
