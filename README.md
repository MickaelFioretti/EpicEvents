# EpicEvents

EpicEvents est une application de gestion d'événements permettant de gérer les utilisateurs, les clients, les contrats et les événements via une interface utilisateur.

## Installation

### Installation avec Docker

#### Prérequis

- Docker
- Docker Compose

1. **Cloner le projet**

    ```bash
    git clone https://github.com/MickaelFioretti/EpicEvents.git
    ```

2. **Construire l'image Docker**

    ```bash
    docker-compose build
    ```

3. **Lancer les conteneurs**

    ```bash
    docker-compose up -d
    ```

4. **Accéder au conteneur**

    ```bash
    docker-compose exec -it epic-events bash
    ```

5. **Accéder au dossier du projet**

    ```bash
    cd /app
    ```

6. **Installer les dépendances**

    ```bash
    poetry install
    ```

7. **Lancer l'application**

    ```bash
    textual run main.py
    ```

### Installation sans Docker

1. **Cloner le projet**

    ```bash
    git clone https://github.com/MickaelFioretti/EpicEvents.git
    ```

2. **Créer un environnement virtuel**

    ```bash
    poetry shell
    ```

4. **Installer les dépendances**

    ```bash
    poetry install
    ```

5. **Lancer l'application**

    ```bash
    textual run main.py
    ```

## Utilisation

### Superuser

```text
username: admin@admin.com
password: changethis
```

### Utilisateur

```text
username: user
password: userpassword
```

## Débogage

Pour activer le mode débogage :

    ```bash
    poetry run textual run --dev main.py
    ```

Dans un autre terminal, exécutez la commande suivante pour lancer le débogueur :

    ```bash
    textual console -x SYSTEM -x EVENT -x DEBUG -x INFO 
    ```
