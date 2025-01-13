# BraveSearch Project

This is the BraveSearch project, consisting of both a frontend and a backend. The project integrates with OpenAI's API, Brave Search API, and a custom Python backend to provide advanced AI-powered features, such as OpenAI chat, Brave search integration, and URL analysis.

## Table of Contents

1. [Frontend Setup](#1-frontend-setup)
2. [Frontend Installation](#2-frontend-installation)
3. [Frontend Usage](#3-frontend-usage)
4. [Backend Setup](#4-backend-setup)
5. [Backend Installation](#5-backend-installation)
6. [Backend Usage](#6-backend-usage)
7. [Contributing](#7-contributing)
8. [License](#8-license)

## Project Overview

This project is a full-stack web application that combines a frontend built using SvelteKit with a backend implemented in FastAPI and Python. It integrates with:

- OpenAI API: For general chat and AI-powered responses.
- Brave Search API: To fetch and enhance search results using AI.
- Custom Python Backend: Crawls and indexes URLs, providing data to the frontend for AI analysis.

### 1. Frontend Setup

## Frontend Prerequisites

Before setting up the frontend, ensure you have the following installed:

- Node.js: Version 23.6.x or higher.
- Bun, NPM, or Yarn: A package manager to install dependencies.

### 2. Frontend Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Falk33n/brave-search.git
   cd frontend
   ```

2. Install dependencies:

   2.1 Using Bun:

   ```bash
   bun install
   ```

   2.2 Using NPM:

   ```bash
   npm install
   ```

   2.3 Using Yarn:

   ```bash
   yarn install
   ```

### 3. Frontend Usage

Run the development server:

1. Using Bun:

```bash
bun run dev
```

2. Using NPM:

```bash
npm run dev
```

3. Using Yarn:

```bash
yarn run dev
```

Open the app in your browser at [http://localhost:3000](http://localhost:3000) to see the frontend in action.

### 4. Backend Setup

## Backend Prerequisites

Before setting up the backend, ensure you have the following installed:

- Python 3.12 (required).
- pip (Python package manager).
- Git (to clone the repository).

### 5.Backend Installation

1. Set Up Python 3.12:

Ensure you're using Python 3.12 for this project. You can check your Python version by running:

```bash
cd backend
python --version
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 6.Backend Usage

Run the FastAPI server:

```bash
uvicorn app.main:app --reload
Access the app at [http://localhost:8000](http://localhost:8000) to interact with the API.
```

The FastAPI docs are available at [http://localhost:8000/docs](http://localhost:8000/docs) for easy testing and exploration of the available endpoints.

### 7. Contributing

Feel free to fork the repository, create issues, or submit pull requests. Contributions are always welcome!

### 8. License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).
