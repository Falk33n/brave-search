# BraveSearch Frontend

This is the frontend for the BraveSearch project, built using SvelteKit. It integrates with OpenAI's API, Brave Search API, and a custom Python backend to deliver advanced AI-powered features such as:

- OpenAI Chat: General chat capabilities using OpenAI models.
- Brave Search API Integration: Leverage search results and enrich responses using AI.
- URL Analysis: Use the Python backend to crawl and index a URL, process its data, and provide AI-generated insights.

### Features

1. OpenAI Integration:

- Seamless communication with OpenAI's GPT models.
- Perform text-based tasks such as summarization, question answering, and more.

2. Brave Search API:

- Retrieve search results and combine them with AI to provide enhanced responses.

3. URL Crawler and Analyzer:

- Interact with the Python backend to index a URL and process its data using AI.

### Prerequisites

- Node.js: Version 23.6.x or higher.
- Bun, NPM or Yarn: Ensure you have a package manager installed.
- Python Backend: The Python backend for URL crawling must be set up and running. See the backend README.md for setup instructions.

### Installation

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
