#!/bin/bash
# Backend Testing Script for CI/CD Pipeline
# Sistema Judicial Digital - Morocco

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Sistema Judicial - Backend Tests         ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Change to backend directory
cd "$(dirname "$0")/.."

# Run unit tests
echo -e "${BLUE}Running Unit Tests...${NC}"
pytest tests/unit/ -v --tb=short || {
    echo -e "${RED}Unit tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Unit tests passed${NC}"
echo ""

# Run integration tests
echo -e "${BLUE}Running Integration Tests...${NC}"
pytest tests/integration/ -v --tb=short || {
    echo -e "${RED}Integration tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Integration tests passed${NC}"
echo ""

# Run API tests
echo -e "${BLUE}Running API Tests...${NC}"
pytest tests/api/ -v --tb=short || {
    echo -e "${RED}API tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ API tests passed${NC}"
echo ""

# Run security tests
echo -e "${BLUE}Running Security Tests...${NC}"
pytest tests/security/ -v --tb=short || {
    echo -e "${RED}Security tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Security tests passed${NC}"
echo ""

# Generate coverage report
echo -e "${BLUE}Generating Coverage Report...${NC}"
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  ✓ All tests completed                    ${NC}"
echo -e "${GREEN}============================================${NC}"
