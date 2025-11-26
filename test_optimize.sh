#!/bin/bash

# Teste da otimização de rota
echo "🧪 Testando endpoint de otimização..."

curl -X POST http://localhost:5000/api/optimize-route \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "2025-01-15",
    "endDate": "2025-01-16",
    "startTime": "18:00",
    "endTime": "23:00",
    "startPoint": "Alexandre"
  }' | jq '{
    success: .success,
    stats: .stats,
    totalBars: (.bars | length),
    totalDays: (.days | length),
    firstBar: .bars[0].name,
    lastBar: .bars[-1].name
  }'
