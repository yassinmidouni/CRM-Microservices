# CRM Microservices System

## 📚 Project Overview
A modern Customer Relationship Management (CRM) system built using a microservices architecture. The project demonstrates practical implementation of microservices concepts using various technologies and programming languages.

## 🎯 Project Goal
The system aims to provide a robust, scalable CRM solution leveraging microservices architecture, demonstrating modern best practices in distributed systems development.

## 🏗️ System Architecture

![Architecture diagram](arechitecture-crm.png)

The system consists of three main microservices interconnected via Dapr and Istio:

### 1. Customer Service
- **Technology**: Node.js/Express
- **Port**: 8085
- **Features**:
  - Customer data management
  - CRUD operations on customer profiles
  - Data validation

### 2. Order Service
- **Technology**: Python/FastAPI
- **Port**: 8087
- **Features**:
  - Order processing
  - Order status tracking
  - Customer service integration

### 3. Notification Service
- **Technology**: Golang
- **Port**: 5001
- **Features**:
  - Real-time notifications
  - Status update tracking

## 🔄 Communication Architecture

### Inter-Service Communication
The system implements a hybrid communication architecture:

#### Dapr (Distributed Application Runtime)
- Event-driven communication between order and notification services
- Pub/sub pattern implementation
- State and secrets management
- Configuration in `./components/pubsub.yaml`

#### Istio Service Mesh
- Traffic management between customer and order services
- Security and observability features
- Intelligent load balancing
- Configuration in `./deploy/destination-rule.yaml` and `./deploy/virtual-service.yaml`

### Infrastructure
- **Kubernetes**: Container orchestration and deployment management
- **Docker Desktop Cluster**: Local development environment

## 💻 Technologies Used

### Languages and Frameworks
- **Customer Service**: Node.js/Express
- **Order Service**: Python/FastAPI
- **Notification Service**: Golang

### Database and Storage
- MongoDB
- Dapr state and secrets persistence

### Infrastructure and Orchestration
- Docker and Docker Compose
- Kubernetes
- Dapr
- Istio Service Mesh

### Monitoring and Observability
- Prometheus
- Grafana
- Dapr tracing

## 🚀 Installation and Deployment

### Prerequisites
```bash
- Docker Desktop with Kubernetes enabled
- Kubectl CLI
- Dapr CLI
- Istio
- Node.js 18+
- Python 3.11+
- Go 1.19+
```

### Infrastructure Setup

1. Kubernetes Cluster Configuration:
```bash
# Check cluster status
kubectl cluster-info
```

2. Dapr Installation:
```bash
# CLI Installation
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize on Kubernetes
dapr init -k
```

3. Istio Installation:
```bash
# Download and install
curl -L https://istio.io/downloadIstio | sh -
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y

# Enable automatic injection
kubectl label namespace default istio-injection=enabled
```

### Services Deployment

1. Dapr Configuration:
```bash
# Deploy Dapr components
kubectl apply -f ./components/pubsub.yaml
```

2. Infrastructure Deployment:
```bash
# MongoDB
kubectl apply -f ./deploy/mongodb.yaml

# Services
kubectl apply -f ./deploy/customer-deployment.yaml
kubectl apply -f ./deploy/order-deployment.yaml
kubectl apply -f ./deploy/notification-deployment.yaml

# Istio Configuration
kubectl apply -f ./deploy/destination-rule.yaml
kubectl apply -f ./deploy/virtual-service.yaml
```

[Rest of the documentation continues with API endpoints, monitoring setup, data structures, testing, etc., following the same structure but without academic references]

## 📜 License
This project is open source and available under the MIT License.
