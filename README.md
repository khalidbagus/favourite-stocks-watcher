# Favorite Stock Watcher

Favorite Stock Watcher is a comprehensive stock analysis application that allows users to compare and monitor their favorite stocks. It leverages modern data processing technologies like Kafka and Spark Streaming to fetch real-time stock data and uses Cassandra for efficient data storage and retrieval. The application provides an interactive dashboard built with Streamlit for data visualization and analysis.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Start Docker Services](#1-start-docker-services)
  - [2. Run the Django Backend](#2-run-the-django-backend)
  - [3. Run the Spark Streaming Script](#3-run-the-spark-streaming-script)
  - [4. Run the Streamlit Dashboard](#4-run-the-streamlit-dashboard)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication**: Secure login and registration system using Streamlit Authenticator.
- **Stock Selection**: Users can select up to three ticker symbols to compare.
- **Real-Time Data Retrieval**: Utilizes Kafka and Spark Streaming to fetch the latest stock reports from the [Sectors API](https://api.sectors.app/).
- **Data Storage**: Stores retrieved stock data in Cassandra for quick access on subsequent requests.
- **Visualization**: Provides interactive visualizations using Streamlit and Altair, including price movements, company overviews, valuation comparisons, dividend comparisons, and financial comparisons.
- **Modular Architecture**: Clean separation of concerns with Django REST API backend and Streamlit frontend.

## Architecture

The application consists of the following components:

- **Django REST API**: Provides backend endpoints to retrieve company information, sectors, and industries.
- **Streamlit Frontend**: User interface for selecting stocks and viewing comparisons.
- **Kafka Producer**: Sends selected ticker symbols to Kafka topics.
- **Spark Streaming**: Consumes ticker symbols from Kafka, fetches stock reports from the Sectors API, and writes data to Cassandra.
- **Cassandra Database**: Stores stock reports for efficient retrieval.
- **Docker Compose**: Orchestrates all services including Zookeeper, Kafka, Spark, and Cassandra.

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine.
- **Python 3.8+**
- **Virtualenv** or **Conda** for managing the Python environment.
- **Git** for cloning the repository.
- **Sectors API Key**: Obtain an API key from [Sectors API](https://api.sectors.app/).
- **PostgreSQL**: For the Django backend database.

## Installation

Follow these steps to set up the project:

### 1. Clone the Repository

```bash
git clone https://github.com/khalidbagus/favourite-stocks-watcher.git
cd favourite-stocks-watcher
```

### 2. Set Up the Virtual Environment

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Python Dependencies

Install the required Python packages:

```bash
pip install -r kafka_venv-requirements.txt
```

### 4. Set Up Environment Variables

#### 4.1 Sectors API Key

Create a `.env` file in the `spark_script` directory with your Sectors API key:

```bash
echo "SECTORS_API_KEY=your_api_key_here" > spark_script/.env
```

Replace `your_api_key_here` with your actual API key from [Sectors API](https://api.sectors.app/).

#### 4.2 Django Settings

Create a `.env` file in the `fsw_project` directory to store your Django settings (e.g., database settings). An example `.env` file:

```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/your_db_name
```

Replace the placeholders with your actual settings.

### 5. Start Docker Services

Ensure Docker and Docker Compose are installed.

Start the services:

```bash
docker-compose up -d
```

This will start:

- Zookeeper
- Kafka
- Spark (Master and Worker)
- Cassandra

### 6. Set Up the Django Backend

Navigate to the Django project directory:

```bash
cd fsw_project
```

#### 6.1 Install PostgreSQL (If Not Using Docker)

If you prefer to use PostgreSQL outside of Docker, install it and create a database.

#### 6.2 Apply Migrations

```bash
python manage.py migrate
```

#### 6.3 Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

#### 6.4 Populate the Database

You need to populate your PostgreSQL database with sectors, subsectors, industries, and companies data. You can:

- Use the Django admin interface at `http://localhost:8000/admin`.
- Create a data migration script.
- Use fixtures to load initial data.

### 7. Set Up Streamlit Authentication

Navigate to the `dashboard` directory:

```bash
cd ../dashboard
```

Create a `config.yaml` file for `streamlit_authenticator`. An example `config.yaml`:

```yaml
credentials:
  usernames:
    john_doe:
      name: John Doe
      password: hashed_password_here
      email: john@example.com

cookie:
  name: streamlit_auth
  key: some_random_key
  expiry_days: 30
```

- Use `streamlit_authenticator` to generate hashed passwords.

### 8. Prepare the Spark Streaming Script

Ensure that the `company_report_streaming.py` script in the `spark_script` directory is configured correctly.

- Verify the Kafka and Cassandra connection settings.
- Ensure the `.env` file with the `SECTORS_API_KEY` is correctly placed in the `spark_script` directory.

## Usage

The application requires running multiple components simultaneously. Follow these steps in order:

### 1. Start Docker Services

If you haven't already started the Docker services during installation, do so now:

```bash
docker-compose up -d
```

### 2. Run the Django Backend

Navigate to the Django project directory and start the server:

```bash
cd fsw_project
python manage.py runserver
```

This starts the Django REST API at `http://localhost:8000`.

### 3. Run the Spark Streaming Script

Open a new terminal window (ensure your virtual environment is activated) and run the Spark Streaming script:

```bash
cd spark_script
python company_report_streaming.py
```

**Note**: The Spark Streaming script must be running continuously to process data from Kafka and write it to Cassandra.

### 4. Run the Streamlit Dashboard

Open another terminal window and navigate to the `dashboard` directory:

```bash
cd dashboard
streamlit run app.py
```

Access the Streamlit dashboard at `http://localhost:8501`.

## Configuration

- **API Keys**

  - Ensure you have your Sectors API key set in the `spark_script/.env` file.

- **Kafka and Spark Configuration**

  - Configurations are set in the `docker-compose.yml` file and `spark_script/company_report_streaming.py`.

- **Streamlit Authentication**

  - User credentials are managed in `dashboard/config.yaml`. You can update this file to manage users.

- **Database Settings**

  - Update your PostgreSQL settings in the `fsw_project/.env` file.

- **Environment Variables**

  - Make sure all `.env` files are correctly placed and contain the necessary keys.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README provides a comprehensive guide to setting up and using the Favorite Stock Watcher application. Remember to run the Spark Streaming script and the Django backend simultaneously before starting the Streamlit dashboard. If you have any questions or encounter any issues, please open an issue on the [GitHub repository](https://github.com/khalidbagus/favourite-stocks-watcher).