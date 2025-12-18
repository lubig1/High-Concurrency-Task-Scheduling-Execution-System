# High-Concurrency Task Scheduling & Execution System

A production-style, high-concurrency task scheduling system built with **Python**, **FastAPI**, **PostgreSQL**, and **Redis**, designed to demonstrate backend engineering best practices such as **idempotency**, **asynchronous processing**, **fault tolerance**, and **observability**.

---

## ✨ Key Features

- **High-Concurrency API**  
  Handles large volumes of concurrent task submissions using asynchronous FastAPI endpoints.

- **Asynchronous Task Execution**  
  Decouples request handling from task execution using Redis-backed worker queues.

- **Idempotent Task Submission**  
  Prevents duplicate task execution via `Idempotency-Key`, a common production requirement in distributed systems.

- **Reliable State Management**  
  Uses PostgreSQL as the single source of truth for task state, avoiding Redis-only persistence pitfalls.

- **Transactional Outbox Pattern**  
  Guarantees consistency between database writes and task enqueueing.

- **Fault Tolerance & Retries**  
  Supports at-least-once execution semantics with configurable retries and failure handling.

- **Rate Limiting & API Security**  
  Protects public APIs using API key authentication and Redis-based rate limiting.

- **Observability**  
  Exposes `/healthz` and `/metrics` endpoints for health checks and Prometheus monitoring.

---

## 🏗 System Architecture

```
Client
  │
  │  REST API (FastAPI)
  ▼
API Service
  │
  │  (Transactional)
  │  ├── PostgreSQL (Task + Outbox tables)
  │  └── Redis Queue (RQ)
  ▼
Worker Pool
  │
  │  Task Execution
  ▼
PostgreSQL (Final Task State)
```

---

## 🧰 Tech Stack

- Language: Python 3.11  
- API Framework: FastAPI  
- Database: PostgreSQL (Async SQLAlchemy)  
- Queue: Redis + RQ  
- Containerization: Docker, Docker Compose  
- Observability: Prometheus-compatible metrics  
- Logging: Structured JSON logging  

---

## 🚀 Getting Started

### Prerequisites
- Docker
- Docker Compose

### Start the System
```bash
docker-compose up --build
```

---

## 📡 API Usage

### Submit a Task
```bash
curl -X POST http://localhost:8000/v1/tasks \
  -H "X-API-Key: change-me" \
  -H "X-Client-Id: demo-user" \
  -H "Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{"task_type":"demo","data":{"msg":"hello"}}'
```

### Query Task Status
```bash
curl http://localhost:8000/v1/tasks/<TASK_ID> \
  -H "X-API-Key: change-me"
```

---

## 📊 Observability

- `GET /healthz` – service and database health check  
- `GET /metrics` – Prometheus-compatible metrics endpoint  

---

## 🧠 Reliability Guarantees

- Idempotent task submission  
- At-least-once task execution  
- Transactional outbox for consistency  

---

## 👨‍💻 Author

Zhaohong Lu  
Backend / Distributed Systems / Python  
