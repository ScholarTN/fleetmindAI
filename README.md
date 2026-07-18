<div align="center">

# 🚛 FleetMind AI

### Intelligent Fleet Management Platform powered by AI

*A modern, scalable Transportation Management System (TMS) built with FastAPI, PostgreSQL, Docker, and AI-ready architecture.*

---

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-blue?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-Authentication-black?style=for-the-badge)

</div>

---

# 📖 Overview

FleetMind AI is an enterprise-grade Fleet Management System designed to help logistics companies manage drivers, trucks, dispatch operations, and fleet intelligence from a single platform.

The project is built with a modern backend architecture following industry best practices including:

- Repository Pattern
- Service Layer Architecture
- JWT Authentication
- RESTful APIs
- Dockerized Infrastructure
- PostgreSQL Database
- Redis Caching
- Alembic Database Versioning

The platform is designed with AI integration in mind, allowing future deployment of intelligent copilots, route optimization, predictive maintenance, and operational analytics.

---

# ✨ Features

## Authentication

- Secure JWT Authentication
- User Registration
- Login
- OAuth2 Support
- Protected Endpoints
- Password Hashing
- Role-ready Architecture

---

## Driver Management

- Create Driver
- Update Driver
- Delete Driver
- Driver Search
- Driver Statistics
- Hours of Service (HOS)
- Safety Metrics
- Driver Availability
- Driver Status Tracking
- Truck Assignment Ready

---

## Truck Management *(In Progress)*

- Truck Profiles
- Fleet Status
- Maintenance Scheduling
- Fuel Monitoring
- Mileage Tracking
- Driver Assignment
- Vehicle Availability

---

## Future AI Features

- AI Fleet Copilot
- Route Optimization
- Predictive Maintenance
- ETA Prediction
- Fuel Consumption Analytics
- Driver Performance Insights
- Natural Language Fleet Assistant
- AI Dispatch Recommendations

---

# 🏗 Architecture

```
                Client
                   │
                   ▼
             FastAPI Backend
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
 Authentication           Business Logic
      │                         │
      ▼                         ▼
 Repository Layer       Service Layer
      │                         │
      └────────────┬────────────┘
                   ▼
            PostgreSQL Database
                   │
                   ▼
                 Redis
```

---

# 📂 Project Structure

```
FleetMind-AI
│
├── alembic/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── docker/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🛠 Tech Stack

| Backend | Database | DevOps | Authentication |
|----------|----------|---------|----------------|
| FastAPI | PostgreSQL | Docker | JWT |
| SQLAlchemy | Alembic | Docker Compose | OAuth2 |
| Pydantic | Redis | GitHub | bcrypt |

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/yourusername/FleetMind-AI.git

cd FleetMind-AI
```

---

## Build Containers

```bash
docker compose up --build
```

---

## Run Database Migrations

```bash
docker compose exec backend alembic upgrade head
```

---

## API Documentation

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# 🔐 Authentication Flow

```
Register
      │
      ▼
Login
      │
      ▼
Receive JWT Token
      │
      ▼
Authorize in Swagger
      │
      ▼
Access Protected APIs
```

---

# 🧩 Current Modules

| Module | Status |
|----------|---------|
| Authentication | ✅ Complete |
| Users | ✅ Complete |
| Driver Management | ✅ Complete |
| JWT Security | ✅ Complete |
| PostgreSQL | ✅ Complete |
| Docker | ✅ Complete |
| Redis | ✅ Complete |
| Truck Management | 🚧 In Progress |
| Dispatch | 📅 Planned |
| AI Copilot | 📅 Planned |
| Route Optimization | 📅 Planned |

---

# 📊 Database

Current entities include:

- Users
- Drivers

Upcoming entities:

- Trucks
- Trailers
- Loads
- Shipments
- Dispatch
- Routes
- Maintenance
- Fuel Logs

---

# 🧪 API Testing

FleetMind provides interactive API documentation using Swagger.

Features tested:

- User Registration
- Login
- JWT Authorization
- Driver CRUD Operations
- Driver Statistics
- Protected Endpoints

---

# 🎯 Project Goals

- Build a scalable enterprise fleet management platform
- Follow clean architecture principles
- Implement production-ready backend practices
- Prepare the platform for AI-powered logistics automation
- Demonstrate modern backend engineering skills

---

# 📈 Roadmap

### Phase 1

- Authentication
- Driver Management
- Truck Management

### Phase 2

- Dispatch System
- Fleet Dashboard
- Route Planning
- Reports

### Phase 3

- AI Fleet Copilot
- Predictive Analytics
- LLM Integration
- Voice Assistant
- Autonomous Workflow Automation

---

# 🤝 Contributing

Contributions, suggestions, and improvements are always welcome.

Please feel free to fork the repository and submit a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

---

<div align="center">

### ⭐ If you found this project interesting, consider giving it a star!

**Built with ❤️ using FastAPI, PostgreSQL, Docker and AI**

</div>
