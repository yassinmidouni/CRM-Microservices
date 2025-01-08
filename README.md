# Système CRM Microservices

## 📚 Présentation du Projet
Ce projet académique est réalisé dans le cadre du cours de développement microservices à l'École Nationale d'Ingénieurs de Tunis (ENIT), sous la supervision du Professeur Mohamed Escheikh.

### 🎓 Informations Académiques
- **Institution**: École Nationale d'Ingénieurs de Tunis (ENIT)
- **Département**: TIC
- **Professeur**: Mr. Mohamed Escheikh
- **Année Académique**: 2024-2025
- **Type de Projet**:  Microservices

## 🎯 Objectif du Projet
Nous avons développé un système CRM (Customer Relationship Management) moderne basé sur une architecture microservices. L'objectif pédagogique est de mettre en pratique les concepts de développement de microservices en utilisant différentes technologies et langages de programmation.

## 🏗️ Architecture du Système

```graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Istio Service Mesh"
            C[Customer Service<br>Node.js/Express<br>:8085]
            O[Order Service<br>Python/FastAPI<br>:8087]
            
            C -->|Istio Routing| O
        end
        
        subgraph "Dapr Runtime"
            O -->|Pub/Sub| D[Dapr Sidecar]
            D -->|Event| N[Notification Service<br>Golang<br>:5001]
        end
        
        subgraph "Base de données"
            DB[(MongoDB)]
            C --> DB
            O --> DB
        end
        
        subgraph "Monitoring"
            P[Prometheus]
            G[Grafana]
            Z[Zipkin]
            
            C -->|Metrics| P
            O -->|Metrics| P
            N -->|Metrics| P
            
            P --> G
            D -->|Traces| Z
        end
    end
```

Notre système est composé de trois microservices principaux interconnectés via Dapr et Istio :

### 1. Service Client (Customer Service)
- **Technologie**: Node.js/Express
- **Port**: 8085
- **Fonctionnalités**:
  - Gestion des données clients
  - Opérations CRUD sur les profils clients
  - Validation des données

### 2. Service Commandes (Order Service)
- **Technologie**: Python/FastAPI
- **Port**: 8087
- **Fonctionnalités**:
  - Traitement des commandes
  - Suivi des statuts de commande
  - Intégration avec le service client

### 3. Service Notifications
- **Technologie**: Golang
- **Port**: 5001
- **Fonctionnalités**:
  - Notifications en temps réel
  - Suivi des mises à jour de statut

## 🔄 Architecture de Communication

### Communication Inter-Services
Nous utilisons une architecture hybride pour la communication entre nos services :

#### Dapr (Distributed Application Runtime)
- Communication événementielle entre le service de commandes et notifications
- Implémentation du modèle pub/sub
- Gestion des états et des secrets
- Configuration dans `./components/pubsub.yaml`

#### Istio Service Mesh
- Gestion du trafic entre les services client et commandes
- Fonctionnalités de sécurité et d'observabilité
- Load balancing intelligent
- Configuration dans `./deploy/destination-rule.yaml` et `./deploy/virtual-service.yaml`

### Infrastructure
- **Kubernetes**: Orchestration des conteneurs et gestion des déploiements
- **Docker Desktop Cluster**: Environnement de développement local

## 💻 Technologies Utilisées

### Langages et Frameworks
- **Service Client**: Node.js/Express
- **Service Commandes**: Python/FastAPI
- **Service Notifications**: Golang

### Base de Données et Stockage
- MongoDB
- Persistance Dapr (état et secrets)

### Infrastructure et Orchestration
- Docker et Docker Compose
- Kubernetes
- Dapr
- Istio Service Mesh

### Monitoring et Observabilité
- Prometheus
- Grafana
- Tracing Dapr

## 🚀 Installation et Déploiement

### Prérequis
```bash
- Docker Desktop avec Kubernetes activé
- Kubectl CLI
- Dapr CLI
- Istio
- Node.js 18+
- Python 3.11+
- Go 1.19+
```

### Configuration de l'Infrastructure

1. Configuration du Cluster Kubernetes :
```bash
# Vérifier l'état du cluster
kubectl cluster-info
```

2. Installation de Dapr :
```bash
# Installation du CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialisation sur Kubernetes
dapr init -k
```

3. Installation d'Istio :
```bash
# Téléchargement et installation
curl -L https://istio.io/downloadIstio | sh -
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y

# Activer l'injection automatique
kubectl label namespace default istio-injection=enabled
```

### Déploiement des Services

1. Configuration Dapr :
```bash
# Déployer les composants Dapr
kubectl apply -f ./components/pubsub.yaml
```

2. Déploiement de l'Infrastructure :
```bash
# MongoDB
kubectl apply -f ./deploy/mongodb.yaml

# Services
kubectl apply -f ./deploy/customer-deployment.yaml
kubectl apply -f ./deploy/order-deployment.yaml
kubectl apply -f ./deploy/notification-deployment.yaml

# Configuration Istio
kubectl apply -f ./deploy/destination-rule.yaml
kubectl apply -f ./deploy/virtual-service.yaml
```

3. Vérification des Déploiements :
```bash
# Vérifier les pods
kubectl get pods

# Vérifier les services
kubectl get svc

# Vérifier les composants Dapr
dapr list -k
```

## 📡 Points d'Accès API

### Service Client (8085)
```
GET    /api/customers            - Liste des clients
GET    /api/customers/:id        - Détails d'un client
POST   /api/customers            - Création d'un client
PUT    /api/customers/:id        - Mise à jour d'un client
DELETE /api/customers/:id        - Suppression d'un client
GET    /metrics                  - Métriques Prometheus
GET    /health                   - Vérification de santé
```

### Service Commandes (8087)
```
GET    /api/orders               - Liste des commandes
GET    /api/orders/:id           - Détails d'une commande
POST   /api/orders               - Création d'une commande
PUT    /api/orders/:id/status    - Mise à jour du statut
DELETE /api/orders/:id           - Suppression d'une commande
GET    /metrics                  - Métriques Prometheus
GET    /health                   - Vérification de santé
```

### Service Notifications (5001)
```
POST   /orders                   - Réception des notifications
GET    /health                   - Vérification de santé
```

## 📊 Surveillance et Métriques

### Installation des Outils de Monitoring

1. Déploiement :
```bash
# Grafana et Prometheus
kubectl apply -f ./samples/addons/grafana.yaml
kubectl apply -f ./samples/addons/prometheus.yaml
```

2. Accès aux Dashboards :
```bash
# Grafana (http://localhost:3000)
kubectl port-forward svc/grafana 3000:3000

# Prometheus (http://localhost:9090)
kubectl port-forward svc/prometheus 9090:9090
```

### Métriques Disponibles
- Compteurs de requêtes par service
- Latence des appels inter-services
- Taux de succès/échec
- Utilisation des ressources
- Métriques personnalisées Dapr

## 👥 Structure des Données

### Client (Customer)
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "phone": "string",
  "address": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Commande (Order)
```json
{
  "id": "string",
  "customer_id": "string",
  "items": [
    {
      "product_name": "string",
      "quantity": "integer",
      "price": "float"
    }
  ],
  "total_price": "float",
  "status": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## 🔍 Tests et Validation

### Exécution des Tests
```bash
# Service Client
cd customer-service
nmp install
npm test

# Service Commandes
cd order-service
pip install requirement.txt
python -m pytest

# Service Notifications
cd notification-service
go mod tidy
go test ./...
```

### Tests d'Intégration
```bash
# Tester la communication Dapr
dapr run --app-id test-pub --app-port 3000 node app.js

# Tester le routage Istio
kubectl apply -f ./test/virtual-service-test.yaml
```

## 📝 Documentation

- Service Client : Documentation Swagger à `/api-docs`
- Service Commandes : Documentation FastAPI à `/docs`
- Service Notifications : Documentation dans le code source
- Dapr : Components et configuration dans `/components`
- Kubernetes : Manifestes de déploiement dans `/deploy`

## ✍️ Auteurs
- Yassin Midouni & Salsabil Moumni & Med Amine Arifi
- Étudiants à l'ENIT
- Télécommunications-I3C
- Promotion [2024/2025]

## 📜 Licence
Ce projet est réalisé à des fins éducatives dans le cadre du cours de développement microservices à l'ENIT.

