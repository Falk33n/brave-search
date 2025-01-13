# Page Crawler

This is a simple web crawler application built using **FastAPI** and **BeautifulSoup4**. It allows users to input a URL, crawl the page, and index the content without following any inner links. This app can be used as a starting point for building more advanced crawlers.

## Table of Contents

1. [Clone the repository](#1-clone-the-repository)
2. [Setup Instructions](#2-set-up-python-312)
3. [Install Dependencies](#3-install-dependencies)
4. [Run the App](#4-run-the-app)
5. [Usage](#5-usage)
6. [Folder Structure](#6-folder-structure)
7. [Contributing](#7-contributing)
8. [License](#8-license)

## Prerequisites

Before you begin, ensure that you have the following installed:

- **Python 3.12** (required)
- **Git** (to clone the repository)
- **pip** (Python package manager)

## Setup Instructions

### 1. Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/Falk33n/brave-search.git
cd backend
```

### 2. Set Up Python 3.12

Ensure that you're using **Python 3.12** for this project. You can check your Python version by running:

```bash
python --version
```

If you're using a virtual environment, ensure it’s using Python 3.12.

### 3. Install Dependencies

Navigate to the project folder and install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

This will install the necessary packages listed in the requirements.txt file.

### 4. Run the App

Once the dependencies are installed, you can run the app using:

```bash
uvicorn app.main:app --reload
```

This command starts a local development server, and the --reload flag allows the server to auto-reload when you make changes to the code.

Once the server is running, you can access the app at:

- [http://localhost:8000](http://localhost:8000)

You should see the FastAPI interactive docs page, where you can interact with the page crawler functionality.

### 5. Usage

To use the page crawler app:

1. Go to [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to access the Swagger UI.
2. In the POST request section, enter the URL you want to crawl.
3. Hit Execute to get a response with the indexed content of the page.

### 6. Folder Structure

Here’s an overview of the project structure:

```bash
backend/
├── app/
│   ├── __init__.py        # Marks the directory as a Python package
│   ├── main.py            # FastAPI app with route definitions
│   ├── crawler.py         # The crawler logic and functions
│   ├── .env               # Environment variables configuration
│   └── utils.py           # Helper functions for parsing or processing data (optional)
├── requirements.txt       # List of required Python packages
├── README.md              # Project overview and documentation
├── LICENSE.md             # License information
└── .gitignore             # Git ignore configuration
```

### 7. Contributing

Feel free to fork the repository, create issues, or submit pull requests. Contributions are welcome!

### 8. License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).
