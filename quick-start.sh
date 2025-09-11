#!/bin/bash

# Onyx Quick Start Script
# One-command setup for testing Onyx locally

set -e

echo "╔════════════════════════════════════════════╗"
echo "║        🚀 Onyx Quick Start Setup          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check prerequisites
check_prerequisites() {
    local missing_deps=0
    
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓ Docker installed${NC}"
    else
        echo -e "${RED}✗ Docker not found${NC}"
        missing_deps=1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo -e "${GREEN}✓ Docker Compose installed${NC}"
    else
        echo -e "${RED}✗ Docker Compose not found${NC}"
        missing_deps=1
    fi
    
    # Check Docker daemon
    if docker info &> /dev/null; then
        echo -e "${GREEN}✓ Docker daemon running${NC}"
    else
        echo -e "${RED}✗ Docker daemon not running${NC}"
        echo -e "${YELLOW}  Please start Docker Desktop or Docker daemon${NC}"
        missing_deps=1
    fi
    
    if [ $missing_deps -eq 1 ]; then
        echo ""
        echo -e "${RED}Please install missing dependencies and try again.${NC}"
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    echo ""
}

# Function to display menu
show_menu() {
    echo "Please select an option:"
    echo ""
    echo "  1) 🏗️  Build and Start Onyx (Full Setup)"
    echo "  2) ⚡ Start Onyx (Using Pre-built Images)"
    echo "  3) 🛑  Stop Onyx"
    echo "  4) 🗑️  Clean Up (Remove containers and volumes)"
    echo "  5) 📊  View Service Status"
    echo "  6) 📝  View Logs"
    echo "  7) 🔄  Restart Services"
    echo "  8) ❌  Exit"
    echo ""
}

# Build and start services
build_and_start() {
    echo -e "${GREEN}Building and starting Onyx...${NC}"
    ./build-and-run.sh
}

# Start with pre-built images
start_prebuilt() {
    echo -e "${GREEN}Starting Onyx with pre-built images...${NC}"
    cd deployment/docker_compose
    
    # Create .env if not exists
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Creating default .env file...${NC}"
        cp ../../build-and-run.sh /tmp/temp-build.sh 2>/dev/null || true
        bash -c 'source /tmp/temp-build.sh 2>/dev/null; true' || true
    fi
    
    docker-compose -f docker-compose.dev.yml pull
    docker-compose -f docker-compose.dev.yml up -d
    
    echo -e "${GREEN}✅ Onyx started!${NC}"
    echo ""
    echo "Access at:"
    echo "  Web UI: http://localhost:3000"
    echo "  API: http://localhost:8080"
}

# Stop services
stop_services() {
    echo -e "${YELLOW}Stopping Onyx services...${NC}"
    cd deployment/docker_compose
    docker-compose -f docker-compose.dev.yml down
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Clean up everything
cleanup() {
    echo -e "${RED}⚠️  This will remove all containers, volumes, and data!${NC}"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd deployment/docker_compose
        docker-compose -f docker-compose.dev.yml down -v --remove-orphans
        echo -e "${GREEN}✅ Cleanup complete${NC}"
    else
        echo "Cleanup cancelled"
    fi
}

# View status
view_status() {
    cd deployment/docker_compose
    echo -e "${BLUE}Service Status:${NC}"
    docker-compose -f docker-compose.dev.yml ps
}

# View logs
view_logs() {
    echo "Select service to view logs:"
    echo "  1) All services"
    echo "  2) API Server"
    echo "  3) Web Server"
    echo "  4) Background Jobs"
    echo "  5) PostgreSQL"
    echo "  6) Back to main menu"
    
    read -p "Choice: " log_choice
    
    cd deployment/docker_compose
    case $log_choice in
        1) docker-compose -f docker-compose.dev.yml logs -f --tail=100 ;;
        2) docker-compose -f docker-compose.dev.yml logs -f --tail=100 api_server ;;
        3) docker-compose -f docker-compose.dev.yml logs -f --tail=100 web_server ;;
        4) docker-compose -f docker-compose.dev.yml logs -f --tail=100 background ;;
        5) docker-compose -f docker-compose.dev.yml logs -f --tail=100 relational_db ;;
        6) return ;;
        *) echo "Invalid option" ;;
    esac
}

# Restart services
restart_services() {
    echo -e "${YELLOW}Restarting services...${NC}"
    cd deployment/docker_compose
    docker-compose -f docker-compose.dev.yml restart
    echo -e "${GREEN}✅ Services restarted${NC}"
}

# Main program
main() {
    check_prerequisites
    
    while true; do
        show_menu
        read -p "Enter your choice (1-8): " choice
        echo ""
        
        case $choice in
            1) build_and_start ;;
            2) start_prebuilt ;;
            3) stop_services ;;
            4) cleanup ;;
            5) view_status ;;
            6) view_logs ;;
            7) restart_services ;;
            8) echo "Goodbye!"; exit 0 ;;
            *) echo -e "${RED}Invalid option. Please try again.${NC}" ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
        clear
    done
}

# Run main program
main
