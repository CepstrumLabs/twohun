# Twohun

Twohun is a web application based on React and FastAPI that displays a list of stocks along with their 50/200 day moving average stock values.

## Features
- Display stock tickers and company names
- Show 50-day and 200-day moving averages
- Real-time data updates from PostgreSQL database

## Project Structure
```
twohun/
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── index.js
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   └── main.py
├── docker/                  # Docker configuration
└── README.md
```

## Setup Instructions

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Database Setup
1. Create PostgreSQL database named 'twohun_db'
2. Update database credentials in backend environment variables

## Docker Deployment
To deploy the entire application stack:
```bash
docker-compose up -d
```

To stop the application:
```bash
docker-compose down
```

To view logs:
```bash
docker-compose logs -f
```

### Development Mode

Development mode provides hot-reloading and debugging features for local development.

To start the development servers:

```bash
make dev
```

This will:
- Start the backend on localhost:8000 with auto-reload enabled
- Launch the frontend dev server on localhost:3000 with hot reloading
- Enable debug mode for both services
- Configure CORS for local development
- Run with a single worker for easier debugging

You can stop both servers at any time by pressing Ctrl+C.

To install all required dependencies before first run:

```bash
make install
```

### Production Mode

Production mode is optimized for performance and security in a deployed environment.

To start the production servers:

```bash
make prod
```

This will:
- Start the backend with multiple workers for better performance
- Build and serve the optimized frontend bundle
- Disable debug mode for security
- Configure CORS for production domain
- Enable production-level logging
- Use production environment variables

Before deploying to production, ensure you have:
1. Updated your production configuration files
2. Set up your environment variables
3. Configured your database settings

You can build the production assets separately with:

```bash
make build ENV=prod
```

To stop the production servers, press Ctrl+C.

### Environment-Specific Configuration

The system uses different configuration files for development and production:

Backend Configuration:
- `backend/app/config/dev.py` - Development settings
  - Local database connection
  - Debug mode enabled
  - CORS for localhost:3000

- `backend/app/config/prod.py` - Production settings
  - Production database connection
  - Debug mode disabled
  - CORS for production domain
  - Multiple workers

Frontend Environment Variables:
- `.env.development`
  - API URL points to localhost:8000
  - Development mode enabled

- `.env.production`
  - API URL points to production domain
  - Production optimizations enabled

To use a specific environment:
```bash
# For development
make dev

# For production
make prod

# For building specific environment
make build ENV=prod
```
