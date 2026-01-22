#!/bin/bash
# Quick test script to run all tests

set -e

echo "🧪 Running Copyright Certificate Extractor Tests"
echo "================================================"
echo

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-cov pytest-mock
fi

# Run tests
echo "📋 Running unit tests..."
python -m pytest tests/ -v --cov=scripts --cov-report=term-missing

echo
echo "✅ All tests completed!"
echo
echo "📊 Test coverage report generated in htmlcov/"
echo "   Open htmlcov/index.html in browser to view detailed coverage"
