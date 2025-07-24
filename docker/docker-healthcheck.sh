#!/bin/bash

# Docker Health Check Script
# This script performs comprehensive health checks for the application

set -e

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Success log
log_success() {
    log "${GREEN}✓ $1${NC}"
}

# Error log
log_error() {
    log "${RED}✗ $1${NC}"
}

# Warning log
log_warning() {
    log "${YELLOW}⚠ $1${NC}"
}

# Check if a service is reachable
check_tcp_port() {
    local host=$1
    local port=$2
    local service_name=$3
    
    if timeout $TIMEOUT bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        log_success "$service_name is reachable at $host:$port"
        return 0
    else
        log_error "$service_name is not reachable at $host:$port"
        return 1
    fi
}

# Check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local service_name=$2
    local expected_status=${3:-200}
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo "000")
    
    if [ "$response_code" -eq "$expected_status" ]; then
        log_success "$service_name HTTP endpoint is healthy ($response_code)"
        return 0
    else
        log_error "$service_name HTTP endpoint is unhealthy (Expected: $expected_status, Got: $response_code)"
        return 1
    fi
}

# Check database connection
check_database() {
    if [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_DB" ]; then
        log "Checking PostgreSQL database connection..."
        
        export PGPASSWORD="$POSTGRES_PASSWORD"
        
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t $TIMEOUT >/dev/null 2>&1; then
            log_success "PostgreSQL database is accessible"
            
            # Check if we can run a simple query
            if psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" >/dev/null 2>&1; then
                log_success "PostgreSQL database query test passed"
                return 0
            else
                log_error "PostgreSQL database query test failed"
                return 1
            fi
        else
            log_error "PostgreSQL database is not accessible"
            return 1
        fi
    else
        log_warning "Database credentials not provided, skipping database check"
        return 0
    fi
}

# Check Redis connection
check_redis() {
    log "Checking Redis connection..."
    
    if command -v redis-cli >/dev/null 2>&1; then
        if [ -n "$REDIS_PASSWORD" ]; then
            local redis_auth="-a $REDIS_PASSWORD"
        else
            local redis_auth=""
        fi
        
        if timeout $TIMEOUT redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" $redis_auth ping >/dev/null 2>&1; then
            log_success "Redis is accessible and responding"
            return 0
        else
            log_error "Redis is not accessible or not responding"
            return 1
        fi
    else
        # If redis-cli is not available, check TCP connection
        check_tcp_port "$REDIS_HOST" "$REDIS_PORT" "Redis"
        return $?
    fi
}

# Check backend API
check_backend() {
    log "Checking backend API..."
    
    # Check health endpoint
    if check_http_endpoint "$BACKEND_URL/api/health/" "Backend API Health"; then
        # Check if Django is responding
        if check_http_endpoint "$BACKEND_URL/api/" "Backend API Root" 404; then
            log_success "Backend API is fully operational"
            return 0
        else
            log_warning "Backend API health check passed but API root is not accessible"
            return 1
        fi
    else
        log_error "Backend API health check failed"
        return 1
    fi
}

# Check frontend
check_frontend() {
    log "Checking frontend application..."
    
    if check_http_endpoint "$FRONTEND_URL" "Frontend Application"; then
        log_success "Frontend application is accessible"
        return 0
    else
        log_error "Frontend application is not accessible"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    log "Checking disk space..."
    
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        log_success "Disk space usage is healthy ($usage%)"
        return 0
    elif [ "$usage" -lt 90 ]; then
        log_warning "Disk space usage is getting high ($usage%)"
        return 0
    else
        log_error "Disk space usage is critical ($usage%)"
        return 1
    fi
}

# Check memory usage
check_memory() {
    log "Checking memory usage..."
    
    if command -v free >/dev/null 2>&1; then
        local mem_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
        local mem_usage_int=$(echo "$mem_usage" | cut -d. -f1)
        
        if [ "$mem_usage_int" -lt 80 ]; then
            log_success "Memory usage is healthy ($mem_usage%)"
            return 0
        elif [ "$mem_usage_int" -lt 90 ]; then
            log_warning "Memory usage is getting high ($mem_usage%)"
            return 0
        else
            log_error "Memory usage is critical ($mem_usage%)"
            return 1
        fi
    else
        log_warning "Memory check tools not available, skipping memory check"
        return 0
    fi
}

# Main health check function
run_health_checks() {
    local failed_checks=0
    
    log "=== Starting Health Checks ==="
    
    # Basic system checks
    check_disk_space || ((failed_checks++))
    check_memory || ((failed_checks++))
    
    # Service checks
    check_database || ((failed_checks++))
    check_redis || ((failed_checks++))
    check_backend || ((failed_checks++))
    check_frontend || ((failed_checks++))
    
    log "=== Health Check Summary ==="
    
    if [ $failed_checks -eq 0 ]; then
        log_success "All health checks passed!"
        return 0
    else
        log_error "$failed_checks health check(s) failed!"
        return 1
    fi
}

# Check if running in Docker
if [ -f /.dockerenv ]; then
    log "Running inside Docker container"
    
    # Determine which service this is based on environment or available commands
    if command -v python >/dev/null 2>&1 && [ -f "manage.py" ]; then
        log "Detected Django backend container"
        check_backend
        exit $?
    elif command -v node >/dev/null 2>&1 && [ -f "package.json" ]; then
        log "Detected Node.js frontend container"
        check_frontend
        exit $?
    elif command -v pg_isready >/dev/null 2>&1; then
        log "Detected PostgreSQL container"
        check_database
        exit $?
    elif command -v redis-cli >/dev/null 2>&1; then
        log "Detected Redis container"
        check_redis
        exit $?
    else
        log_warning "Could not determine container type, running basic checks"
        check_disk_space && check_memory
        exit $?
    fi
else
    log "Running comprehensive health checks"
    run_health_checks
    exit $?
fi 