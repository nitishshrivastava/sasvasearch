#!/bin/bash

# Onyx Deployment Test Script
# Verifies that all services are running correctly

set -e

echo "🧪 Testing Onyx Deployment..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test function
test_service() {
    local service_name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Testing $service_name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 15

# Run tests
echo ""
echo "Running service tests:"
echo "----------------------"

failed_tests=0

# Test Web UI
if ! test_service "Web UI" "http://localhost:3000" "200\|302\|301"; then
    ((failed_tests++))
fi

# Test API Server
if ! test_service "API Server" "http://localhost:8080/health" "200"; then
    ((failed_tests++))
fi

# Test API Docs
if ! test_service "API Documentation" "http://localhost:8080/docs" "200"; then
    ((failed_tests++))
fi

# Test PostgreSQL
echo -n "Testing PostgreSQL... "
if docker exec sasvasearch-relational_db-1 pg_isready -U postgres &>/dev/null || \
   docker exec deployment-relational_db-1 pg_isready -U postgres &>/dev/null || \
   docker exec docker_compose-relational_db-1 pg_isready -U postgres &>/dev/null; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    ((failed_tests++))
fi

# Test Redis
echo -n "Testing Redis... "
if docker exec sasvasearch-cache-1 redis-cli ping &>/dev/null || \
   docker exec deployment-cache-1 redis-cli ping &>/dev/null || \
   docker exec docker_compose-cache-1 redis-cli ping &>/dev/null; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    ((failed_tests++))
fi

# Summary
echo ""
echo "----------------------"
if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "🎉 Onyx is ready for testing!"
    echo ""
    echo "Access points:"
    echo "  📱 Web Interface: http://localhost:3000"
    echo "  🔌 API: http://localhost:8080"
    echo "  📚 API Docs: http://localhost:8080/docs"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Create an account or login (auth might be disabled)"
    echo "  3. Try the search and chat features"
    echo "  4. Add connectors to index your data"
else
    echo -e "${RED}⚠️  $failed_tests test(s) failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if all containers are running:"
    echo "     docker ps"
    echo "  2. View logs for failed services:"
    echo "     docker-compose -f deployment/docker_compose/docker-compose.dev.yml logs"
    echo "  3. Ensure ports are not already in use"
fi
