#!/bin/bash

# Script para testar a API de Otimização de Rotas

API_URL="http://localhost:5000"

echo "======================================"
echo "Testando API de Otimização de Rotas"
echo "======================================"
echo ""

# 1. Health Check
echo "1. Health Check..."
curl -s "${API_URL}/api/health" | python3 -m json.tool
echo ""
echo ""

# 2. Listar bares (primeiros 5)
echo "2. Listando primeiros 5 bares..."
curl -s "${API_URL}/api/bars" | python3 -m json.tool | head -30
echo "..."
echo ""
echo ""

# 3. Otimizar rota
echo "3. Otimizando rota..."
curl -s -X POST "${API_URL}/api/optimize-route" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "2025-11-25",
    "endDate": "2025-11-27",
    "startTime": "16:00",
    "endTime": "23:00",
    "startPoint": "Alexan'"'"'s Bar",
    "minRating": 4.0
  }' | python3 -m json.tool
echo ""
echo ""

# 4. Buscar coordenadas de um bar
echo "4. Buscando coordenadas do Alexandre's Bar..."
curl -s "${API_URL}/api/bar-coordinates/Alexandre's%20Bar" | python3 -m json.tool
echo ""
echo ""

echo "======================================"
echo "Testes concluídos!"
echo "======================================"
