# 🚀 Onyx Build and Test Instructions

This document provides comprehensive instructions for building and testing the Onyx application locally.

## �� Prerequisites

Before you begin, ensure you have the following installed:

1. **Docker** (version 20.10 or higher)
   - [Install Docker](https://docs.docker.com/get-docker/)
   
2. **Docker Compose** (version 2.0 or higher)
   - Usually comes with Docker Desktop
   - [Install Docker Compose](https://docs.docker.com/compose/install/)

3. **System Requirements**
   - RAM: Minimum 8GB (16GB recommended)
   - Disk Space: At least 20GB free
   - CPU: 4+ cores recommended

## 🎯 Quick Start (Easiest Method)

We've created an interactive quick-start script that handles everything for you:

```bash
# Run the interactive setup
./quick-start.sh
```

This will present you with a menu to:
- Build and start the application
- Stop services
- View logs
- Check status
- And more!

## 🔨 Manual Build and Run

If you prefer to build and run manually:

### Step 1: Build and Start All Services

```bash
# Run the build script
./build-and-run.sh
```

This script will:
1. Check for Docker and Docker Compose
2. Create a default `.env` configuration
3. Build all Docker images
4. Start all services
5. Display access URLs

### Step 2: Access the Application

Once running, you can access:

- **Web UI**: http://localhost:3000
- **API Documentation**: http://localhost:8080/docs
- **Admin Panel**: http://localhost:3000/admin (if auth is disabled)

## 🐳 Docker Compose Commands

For more control, you can use Docker Compose directly:

```bash
# Navigate to the docker compose directory
cd deployment/docker_compose

# Build images
docker-compose -f docker-compose.dev.yml build

# Start services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (clean slate)
docker-compose -f docker-compose.dev.yml down -v
```

## 🧪 Testing the Application

### 1. Basic Functionality Test

Once the application is running:

1. **Open the Web UI**: Navigate to http://localhost:3000
2. **Create an Account**: If auth is enabled, create a test account
3. **Test Search**: Try searching for content
4. **Test Chat**: Use the AI chat interface

### 2. API Testing

Test the API directly:

```bash
# Check API health
curl http://localhost:8080/health

# Get API documentation
# Open http://localhost:8080/docs in your browser
```

### 3. Connector Testing

1. Navigate to Admin Panel
2. Go to "Connectors" section
3. Try adding a simple connector (e.g., Web connector with a public URL)

### 4. Database Access

If you need to access the PostgreSQL database:

```bash
# Connect to PostgreSQL
docker exec -it sasvasearch-relational_db-1 psql -U postgres -d onyx

# Or use any PostgreSQL client with:
# Host: localhost
# Port: 5432
# User: postgres
# Password: password
# Database: onyx
```

## 📊 Service Architecture

The application consists of several services:

| Service | Port | Description |
|---------|------|-------------|
| Web Server | 3000 | Next.js frontend |
| API Server | 8080 | FastAPI backend |
| PostgreSQL | 5432 | Main database |
| Vespa | 8081 | Search engine |
| Redis | 6379 | Cache and queue |
| MinIO | 9004/9005 | S3-compatible storage |
| Model Servers | Internal | NLP model serving |

## 🔧 Configuration

### Environment Variables

The application uses environment variables for configuration. Key variables:

- `AUTH_TYPE`: Authentication method (disabled, basic, google_oauth)
- `GEN_AI_API_KEY`: OpenAI API key for AI features
- `LOG_LEVEL`: Logging verbosity (debug, info, warning, error)

Edit `deployment/docker_compose/.env` to customize.

### Adding AI Capabilities

To enable AI features:

1. Get an API key from [OpenAI](https://platform.openai.com)
2. Edit the `.env` file:
   ```
   GEN_AI_API_KEY=your-api-key-here
   ```
3. Restart services

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check service status
docker-compose -f deployment/docker_compose/docker-compose.dev.yml ps

# View logs for specific service
docker-compose -f deployment/docker_compose/docker-compose.dev.yml logs api_server
```

### Port Already in Use

If you get port conflict errors:

```bash
# Find what's using the port (example for port 3000)
lsof -i :3000

# Kill the process or change the port in docker-compose.dev.yml
```

### Low Memory Issues

If services crash due to memory:

1. Increase Docker memory allocation in Docker Desktop settings
2. Reduce service resource usage by setting limits in docker-compose

### Database Connection Issues

```bash
# Reset the database
docker-compose -f deployment/docker_compose/docker-compose.dev.yml down -v
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d
```

## 📝 Development Mode

For development with hot-reload:

```bash
# Backend development
cd backend
pip install -r requirements/default.txt
uvicorn onyx.main:app --reload --host 0.0.0.0 --port 8080

# Frontend development
cd web
npm install
npm run dev
```

## 🛑 Stopping and Cleanup

### Stop Services (Keep Data)
```bash
docker-compose -f deployment/docker_compose/docker-compose.dev.yml down
```

### Complete Cleanup (Remove Everything)
```bash
docker-compose -f deployment/docker_compose/docker-compose.dev.yml down -v --remove-orphans
docker system prune -a  # Optional: Remove all unused Docker resources
```

## 📚 Additional Resources

- [Onyx Documentation](https://docs.onyx.app/)
- [GitHub Repository](https://github.com/onyx-dot-app/onyx)
- [Discord Community](https://discord.gg/TDJ59cGV2X)
- [Slack Community](https://join.slack.com/t/onyx-dot-app/shared_invite/zt-34lu4m7xg-TsKGO6h8PDvR5W27zTdyhA)

## 💡 Tips

1. **First Time Setup**: The initial build might take 10-15 minutes as it downloads all dependencies
2. **Resource Usage**: The full stack uses about 4-6GB of RAM when running
3. **Model Downloads**: The first run will download NLP models (~1GB)
4. **Development**: Use the dev compose file for local development with hot-reload

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs [service_name]`
2. Review the [documentation](https://docs.onyx.app/)
3. Ask in the [Discord community](https://discord.gg/TDJ59cGV2X)
4. Open an issue on [GitHub](https://github.com/onyx-dot-app/onyx/issues)

---

Happy testing! 🎉
