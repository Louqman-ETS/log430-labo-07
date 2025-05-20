# LOG430 - Labo 01

## Description du projet

Ce projet est réalisé dans le cadre du cours LOG430 – Architecture Logicielle à l’ÉTS. Il consiste à développer un système de caisse simple pour un petit magasin de quartier, en utilisant une architecture client/serveur à deux niveaux (2-tier).

## Instructions de build et d’exécution

### Prérequis
| Outil | Version conseillée | Rôle |
|-------|-------------------|------|
| Python | ≥ 3.13 | Exécution locale & tests |
| Docker | ≥ 24 | Conteneurisation |
| Git | ≥ 2.40 | Gestion de version |
|VS Code | – | IDE prêt pour Docker |

### Étapes pour construire le projet

1. Clonez le dépôt :
     ```bash
     git clone https://github.com/Louqman-ETS/log430-labo-0.git
     cd log430-labo-0
     ```
     
### Exécution sans Docker

1. Lancez l'application :
     ```bash
     python src/main.py
     ```
     
### Build & run avec Docker

1. Construction de l’image :
    ```bash
     docker build -t hello-cli .
     ```

2. Exécution éphémère :
   ```bash
     docker run --rm hello-cli
   ```
### Orchestration avec Docker Compose

1. lance le service "hello" :
    ```bash
     docker compose up --build 
    ```

3. arrêt + suppression du conteneur :

   ```bash
     docker compose down
   ```

## Fonctionnement de la CI/CD

| Étape               | Outils                   | Description                                                                    |
| ------------------- | ------------------------ | ------------------------------------------------------------------------------ |
| **Lint**            | Black –check, Pylint     | Vérifie la conformité stylistique et repère les erreurs potentielles.          |
| **Tests unitaires** | Pytest                   | Exécute deux tests sur la sortie du script et son code de retour.              |
| **Build Docker**    | docker/build‑push‑action | Construit l’image à partir du `Dockerfile`.                                    |
| **Push Docker Hub** | docker/login‑action      | Publie les tags `latest` et `SHA court` vers `docker.io/louqmas/log430-labo-0`. |

> Les identifiants Docker Hub sont fournis au workflow via deux secrets du dépôt :
> DOCKERHUB_USERNAME et DOCKERHUB_TOKEN.

> Le fichier de configuration CI/CD se trouve dans `.github/workflows/ci.yml` .

## Choix techniques

| Élément                | Justification                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------- |
| **Python**             | Langage simple ; parfait pour démontrer la chaîne CI/CD sans surcharge.               |
| **Docker (Slim 3.13)** | Isolation de l’app.                                                                   |
| **Docker Compose**     | Point d’entrée unique ; permettra d’ajouter d’autres services.                        |
| **GitHub Actions**     | Intégration native avec GitHub ; gratuit pour projets publics.                        |
| **Black**              | Formatage automatique, déterministe.                                                  |
| **Pylint**             | Analyse statique : noms incohérents, imports inutiles, etc.                           |
| **Pytest**             | Syntaxe concise, exécution rapide.                                                    |

## Auteurs

- Louqman Masbahi
