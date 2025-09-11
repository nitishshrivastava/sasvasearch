#!/bin/bash

echo "🧹 Docker Disk Space Management"
echo "================================"
echo ""

# Show current Docker disk usage
echo "📊 Current Docker disk usage:"
docker system df
echo ""

# Ask user what to do
echo "Choose an option to free up space:"
echo "  1) Clean up unused Docker resources (Recommended)"
echo "  2) Remove ALL Docker data (Complete reset)"
echo "  3) Skip cleanup"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🧹 Cleaning up unused Docker resources..."
        docker system prune -a --volumes -f
        echo "✅ Cleanup complete!"
        ;;
    2)
        echo "⚠️  WARNING: This will remove ALL Docker containers, images, and volumes!"
        read -p "Are you sure? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            docker stop $(docker ps -aq) 2>/dev/null || true
            docker rm $(docker ps -aq) 2>/dev/null || true
            docker rmi $(docker images -q) 2>/dev/null || true
            docker volume rm $(docker volume ls -q) 2>/dev/null || true
            docker system prune -a --volumes -f
            echo "✅ Complete Docker reset done!"
        else
            echo "Cancelled"
        fi
        ;;
    3)
        echo "Skipping cleanup"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

echo ""
echo "📊 Docker disk usage after cleanup:"
docker system df
echo ""
echo "💡 TIP: If you still have space issues, you may need to:"
echo "   1. Increase Docker Desktop's disk allocation in Settings > Resources"
echo "   2. Free up space on your Mac's main disk"
