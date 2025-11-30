#!/bin/bash

# Investment Dashboard - Quick Health Check
# Usage: bash health-check.sh

echo "======================================"
echo "Investment Dashboard - Health Check"
echo "======================================"

# Check if service is active
echo ""
echo "Service Status:"
sudo systemctl status investment-dashboard

# Check Docker container
echo ""
echo "Docker Container Status:"
docker ps | grep investment-dashboard || echo "Container not running"

# Check port
echo ""
echo "Port 8501 Status:"
sudo lsof -i :8501 || echo "Port not in use"

# Check Docker logs (last 20 lines)
echo ""
echo "Recent Docker Logs:"
docker logs --tail 20 investment-dashboard 2>/dev/null || echo "No logs available"

# Check system logs (last 20 lines)
echo ""
echo "Recent System Logs:"
sudo journalctl -u investment-dashboard -n 20 --no-pager

# Check AWS connectivity
echo ""
echo "AWS Connectivity:"
docker exec investment-dashboard aws dynamodb list-tables --region ap-south-1 2>/dev/null || echo "AWS connection check skipped"

# Check application response
echo ""
echo "Application Response:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8501 || echo "Application not responding"

echo ""
echo "======================================"
