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

#### Setup
1. Create required directories:
```bash
mkdir -p prometheus
```

2. Start development stack with monitoring:
```bash
make dev
```

#### Monitoring Tools

**Local Development Monitoring**
- Prometheus: http://localhost:9090
- Database Metrics: http://localhost:9187/metrics
- API Documentation: http://localhost:8000/docs
- API Metrics: http://localhost:8000/metrics

**View Monitoring Dashboard**
```bash
make monitor
```

#### Development Database
```bash
# Reset development database
make db-reset

# View database logs
docker-compose logs -f db

# Connect to database
psql -h localhost -U twohun -d twohun_db
```

#### Debugging Tips
- Check API logs for database queries
- Monitor connection pool usage
- Watch for N+1 query problems
- Use API metrics for performance optimization
- Enable SQL query logging for development

#### Development Notes
- Monitoring endpoints are only enabled in development
- Database credentials are in .env file
- Hot-reload is enabled for both frontend and backend
- API documentation updates automatically
- Database changes require manual reset

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

### Stock Data API

The application provides endpoints to fetch and store historical stock data:

#### Endpoints

1. Get Stock History
```bash
# Get last 7 days of data for all stocks
GET /api/stocks

# Get specific number of days
GET /api/stocks?days=14
```

2. Add New Stock Data
```bash
# Fetch last 7 days of data for a stock
POST /api/stocks/AAPL

# Fetch specific number of days
POST /api/stocks/AAPL?days=14
```

#### Data Model
Each stock entry contains:
- Ticker symbol
- Company name
- Date
- Closing price
- 50-day moving average
- 200-day moving average

#### Notes
- New data points are added as separate entries
- Duplicate entries (same ticker and date) are prevented
- Historical data is preserved
- Moving averages are calculated using 200 days of historical data

### Stock Data Management Scripts

You can add new stock data using the provided utility script:

```bash
# Add 7 days of data for one or more stocks
python backend/scripts/add_stocks.py AAPL MSFT GOOGL

# Add specific number of days
python backend/scripts/add_stocks.py AAPL MSFT --days 14

# Use different API URL (e.g., production)
python backend/scripts/add_stocks.py AAPL --url https://api.yourdomain.com
```

The script will:
- Add historical data for each specified stock
- Skip any existing entries (no duplicates)
- Report success or failure for each stock

### Monitoring

The application includes comprehensive database monitoring using Prometheus.

#### Setup
1. Create required directories:
```bash
mkdir -p prometheus
mkdir -p backups
chmod +x scripts/backup.sh scripts/restore.sh
```

2. Start production stack:
```bash
make prod
```

#### Database Operations

**Backups**
```bash
# Create manual backup
make backup

# Set up daily backups (2 AM)
crontab -e
# Add: 0 2 * * * cd /path/to/your/project && ./scripts/backup.sh
```

**Restore**
```bash
make restore file=backups/backup_20240321_123456.sql.gz
```

#### Monitoring Dashboards
- Prometheus: http://localhost:9090
- Database Metrics: http://localhost:9187/metrics

View monitoring dashboard:
```bash
make monitor
```

#### Container Management
```bash
# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Important Notes
- Never commit `.env.prod` to version control
- Test restore procedures regularly
- Keep multiple backup copies
- Monitor disk space and connection count
- Set up alerts for critical metrics
- Enable SSL for database connections
- Regular security audits