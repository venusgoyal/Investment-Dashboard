#!/bin/bash

# Investment Dashboard - Logs Monitor
# Usage: bash logs.sh [option]
# Options: systemd, docker, both, tail

OPTION=${1:-both}

case $OPTION in
    systemd)
        echo "Systemd Service Logs (Real-time):"
        sudo journalctl -u investment-dashboard -f
        ;;
    docker)
        echo "Docker Container Logs (Real-time):"
        docker logs -f investment-dashboard
        ;;
    both)
        echo "Systemd Logs:"
        sudo journalctl -u investment-dashboard -n 50 --no-pager
        echo ""
        echo "Docker Logs:"
        docker logs --tail 50 investment-dashboard
        ;;
    tail)
        echo "Last 100 lines of systemd logs:"
        sudo journalctl -u investment-dashboard -n 100 --no-pager
        ;;
    *)
        echo "Usage: bash logs.sh [systemd|docker|both|tail]"
        exit 1
        ;;
esac
