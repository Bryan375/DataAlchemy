# Data Alchemy

Data Alchemy is a powerful data type inference and conversion tool that helps you manage and transform your datasets with ease. It automatically detects data types in your CSV and Excel files, allows you to modify column types, and ensures data consistency across your datasets.

## Features

- 🔍 Automatic data type inference
- 🔄 Real-time type conversion
- 📊 Support for CSV and Excel files
- 🚀 Asynchronous processing for large datasets
- 📱 Responsive web interface
- 🔄 Progress tracking for long-running operations

## Prerequisites

Before running the application, make sure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/data-alchemy.git
cd data-alchemy
```

2. Create a `.env` file in the root directory:
```env
# Database Configuration
DB_NAME=data_alchemy
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
```

3. Build and start the containers:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Project Structure

```
data-alchemy/
├── data_alchemy_fe/     # Frontend React/TypeScript application
├── data_alchemy_be/     # Backend Django application
├── docker-compose.yml   # Docker compose configuration
└── .env                 # Environment variables
```

## Architecture

The application uses:
- Frontend: React with TypeScript and Vite
- Backend: Django with Django REST Framework
- Database: PostgreSQL
- Task Queue: Celery with Redis
- Containerization: Docker

## API Endpoints

- `POST /api/v1/datasets/`: Upload a new dataset
- `GET /api/v1/datasets/{id}/`: Get dataset details
- `PUT /api/v1/columns/{column_id}/type_conversion/`: Update column type
- `GET /api/v1/datasets/{id}/status/?job_id={job_id}`: Check processing status

## Development

The project uses Docker volumes for hot-reloading:
- Frontend code changes will automatically refresh the browser
- Backend code changes will automatically restart the Django development server

