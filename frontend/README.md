# BraveSearch Frontend

This is the frontend for the BraveSearch project, built using SvelteKit. It integrates with OpenAI's API, Brave Search API, and a custom Python backend to deliver advanced AI-powered features such as:

- OpenAI Chat: General chat capabilities using OpenAI models.
- Brave Search API Integration: Leverage search results and enrich responses using AI.
- URL Analysis: Use the Python backend to crawl and index a URL, process its data, and provide AI-generated insights.

## Table of Contents

1. [Features](#1-features)
2. [Installation](#2-installation)
3. [Folder Structure](#3-folder-structure)
4. [How It Works](#4-how-it-works)
5. [Deployment](#5-deployment)
6. [Contributing](#6-contributing)
7. [License](#7-license)

## Prerequisites

- Node.js: Version 23.6.x or higher.
- Bun, NPM or Yarn: Ensure you have a package manager installed.
- Python Backend: The Python backend for URL crawling must be set up and running. See the backend README.md for setup instructions.

### 1. Features

1. OpenAI Integration:

- Seamless communication with OpenAI's GPT models.
- Perform text-based tasks such as summarization, question answering, and more.

2. Brave Search API:

- Retrieve search results and combine them with AI to provide enhanced responses.

3. URL Crawler and Analyzer:

- Interact with the Python backend to index a URL and process its data using AI.

### 3. Installation

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

3. Set Up Environment Variables: Create a .env file in the root directory and configure the following:

```bash
SECRET_OPENAI_KEY=your-openai-api-key
SECRET_BRAVE_KEY=your-brave-search-api-key
SECRET_BACKEND_URL=http://localhost:8000
```

4. Run the Development Server:

   4.1 Using Bun:

   ```bash
   bun run dev
   ```

   4.2 Using NPM:

   ```bash
   npm run dev
   ```

   4.3 Using Yarn:

   ```bash
   yarn run dev
   ```

### 4. Folder Structure

```bash
frontend/
├── src/
│   ├── lib/
│   │   ├── schemas/
│   │   │   ├── brave-search-params-schemas.ts    # Schemas for Brave Search API parameters
│   │   │   ├── index.ts                          # Index file for nicer imports
│   │   │   └── schemas.ts                        # General schemas
│   │   ├── server/
│   │   │   └── utils.ts                          # General server-only utility functions
│   │   └── utils.ts                              # General utility functions
│   ├── routes/
│   │   ├── api/
│   │   │   ├── chat/
│   │   │   │   └── +server.ts                    # Server logic for chat API
│   │   │   ├── search/
│   │   │   │   └── +server.ts                    # Server logic for search API
│   │   │   └── chat-provider/
│   │   │       └── +server.ts                    # Server logic for chat provider API
│   │   ├── +layout.svelte                        # Layout for the application
│   │   └── +page.svelte                          # Main page of the app (Home)
│   ├── app.css                                   # Global CSS styles
│   ├── app.d.ts                                  # Global Svelte-specific types
│   └── app.html                                  # Root HTML file
├── static/
│   └── favicon.png                               # Favicon for the website
├── vite.config.ts                                # Vite configuration (build settings, plugins, etc.)
├── tsconfig.json                                 # TypeScript configuration
├── tailwind.config.ts                            # Tailwind CSS configuration
├── svelte.config.js                              # SvelteKit configuration
├── README.md                                     # Project documentation
├── LICENSE.MD                                    # License information
├── postcss.config.js                             # PostCSS configuration for CSS processing
├── package.json                                  # Package dependencies and scripts
├── bun.lockb                                     # Bun lock file (dependency manager)
├── .prettierrc                                   # Prettier configuration for code formatting
├── .prettierignore                               # Files/folders to ignore for Prettier
├── .env                                          # Environment variables (e.g., OpenAI API key, backend URL)
└── .gitignore                                    # Files/folders to ignore by Git
```

### 5. How It Works

1. Chat with OpenAI:

- The frontend sends user queries to OpenAI using the SECRET_OPENAI_KEY.
- Responses are displayed in a chat-like interface.

2. Brave Search Integration:

- Perform a search via Brave Search API.
- Combine results with OpenAI's GPT to generate enhanced answers.

3. URL Analysis:

- Send a URL to the Python backend for crawling.
- Analyze the data using OpenAI's GPT for summaries, key insights, and more.

### 6. Deployment

1. Build for Production:
   1.1 Using Bun:

   ```bash
   bun run build
   ```

   1.2 Using NPM:

   ```bash
   npm run build
   ```

   1.3 Using Yarn:

   ```bash
   yarn run build
   ```

2. Deploy to your favorite hosting platform (e.g., Vercel, Netlify).

### 7. Contributing

Feel free to fork the repository, create issues, or submit pull requests. Contributions are welcome!

### 8. License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).
