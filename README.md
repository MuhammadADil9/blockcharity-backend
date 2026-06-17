# BloCharity FastAPI Backend

This repository contains the FastAPI backend for **BloCharity**, a decentralized, blockchain-powered charity platform. It serves as the bridge between the frontend application, the smart contracts, and off-chain data processing.

## 🌟 Overview

The backend is built with Python and [FastAPI](https://fastapi.tiangolo.com/), providing a robust, high-performance API for managing campaign metadata, off-chain interactions, donor analytics, and proxying specific requests.

### Key Features
- **Campaign Management:** Tracking campaign lifecycles (active, voting, completed).
- **Voting Integration:** API endpoints to facilitate the donor voting process (e.g., `/api/campaigns/{id}/vote`).
- **Analytics & Tracking:** Providing data for "My Impact" dashboards and donation history.
- **Off-chain Metadata:** Storing extended data that doesn't need to be on the blockchain.

## 📂 Project Structure

The source code is located in the `src/` directory and follows a standard modular FastAPI structure:

- `src/api/` - FastAPI routers and endpoint definitions.
- `src/services/` - Core business logic and smart contract interaction layers.
- `src/models/` - Database models/entities.
- `src/schemas/` - Pydantic models for request/response validation.
- `src/repositories/` - Data access layer.
- `src/config/` - Configuration settings and environment variable management.
- `src/utils/` - Shared utility functions and helpers.
- `src/app.py` - The main FastAPI application entry point.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A running local blockchain node (e.g., Anvil) if testing contract interactions.
- Redis / Database (depending on specific configuration in `.env`).

### Installation

1. **Clone the repository and navigate to the project directory:**
   ```bash
   cd blocharity-fastapi-backend
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the `src/` directory (or root, depending on your loader) and configure necessary variables (RPC URLs, database URIs, API keys, etc.).
   *Note: Never commit your `.env` file. It is ignored by git.*

### Running the Application

You can start the FastAPI development server using `uvicorn`:

```bash
uvicorn src.app:app --reload
```
Alternatively, if using the `fastapi` CLI (available in newer FastAPI versions):
```bash
fastapi dev src/app.py
```

The API will be available at `http://127.0.0.1:8000`.

### API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can access:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

## 🔗 Related Repositories
- **BloCharity Frontend:** React/TypeScript Vite application.
- **BloCharity Smart Contracts:** Solidity contracts managed via Foundry/Anvil.

## 📜 License
This project is part of the BloCharity platform. (Add appropriate license details here).
