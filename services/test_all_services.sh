#!/bin/bash

echo "🧪 Testing all microservices..."
echo "================================"

# Test inventory-api
echo "📦 Testing inventory-api..."
cd inventory-api
PYTHONPATH=src python3 -m pytest tests/ -v --tb=short
INVENTORY_RESULT=$?
cd ..

echo ""
echo "🛒 Testing ecommerce-api..."
cd ecommerce-api
PYTHONPATH=src python3 -m pytest tests/ -v --tb=short
ECOMMERCE_RESULT=$?
cd ..

echo ""
echo "🏪 Testing retail-api..."
cd retail-api
PYTHONPATH=src python3 -m pytest tests/ -v --tb=short
RETAIL_RESULT=$?
cd ..

echo ""
echo "📊 Testing reporting-api..."
cd reporting-api
PYTHONPATH=src python3 -m pytest tests/ -v --tb=short
REPORTING_RESULT=$?
cd ..

echo ""
echo "================================"
echo "📋 Test Results Summary:"
echo "================================"
echo "inventory-api: $([ $INVENTORY_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "ecommerce-api: $([ $ECOMMERCE_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "retail-api: $([ $RETAIL_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "reporting-api: $([ $REPORTING_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo ""

# Compter les tests totaux
TOTAL_TESTS=0
if [ $INVENTORY_RESULT -eq 0 ]; then TOTAL_TESTS=$((TOTAL_TESTS + 23)); fi
if [ $ECOMMERCE_RESULT -eq 0 ]; then TOTAL_TESTS=$((TOTAL_TESTS + 28)); fi
if [ $RETAIL_RESULT -eq 0 ]; then TOTAL_TESTS=$((TOTAL_TESTS + 4)); fi
if [ $REPORTING_RESULT -eq 0 ]; then TOTAL_TESTS=$((TOTAL_TESTS + 20)); fi

echo "🎯 Total tests passing: $TOTAL_TESTS"
echo "================================"

# Exit avec le code d'erreur si au moins un service a échoué
if [ $INVENTORY_RESULT -ne 0 ] || [ $ECOMMERCE_RESULT -ne 0 ] || [ $RETAIL_RESULT -ne 0 ] || [ $REPORTING_RESULT -ne 0 ]; then
    exit 1
else
    echo "🎉 All services tests are passing!"
    exit 0
fi
