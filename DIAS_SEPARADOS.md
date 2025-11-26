# 📅 Organização de Bares por Dia - Documentação

## 🎯 Visão Geral

A aplicação agora organiza a rota otimizada em **múltiplos dias**, com cada dia tendo uma **cor específica** que é usada tanto na barra lateral quanto no mapa.

## 🔧 Mudanças Implementadas

### 1. **Backend (API) - `/comp-evol-tp1/api.py`**

#### Endpoint `/api/optimize-route` - Nova Estrutura de Resposta

A API agora retorna os dados organizados em duas estruturas:

1. **Lista flat** (`bars`): Para compatibilidade retroativa
2. **Lista por dia** (`days`): Nova estrutura com cores e agrupamento

```json
{
  "success": true,
  "bars": [...],  // Lista flat de todos os bares (compatibilidade)
  "days": [       // Nova estrutura organizada por dia
    {
      "date": "2025-01-15",
      "displayDate": "15/01/2025",
      "dayNumber": 1,
      "color": "#FF6B6B",  // Cor específica do dia
      "bars": [
        {
          "id": 1,
          "name": "Alexandre's Bar",
          "lat": -19.932821,
          "lng": -43.945123,
          "arrivalTime": "18:00",
          "rating": 4.5,
          "address": "..."
        }
      ]
    }
  ],
  "stats": {
    "totalDistance": "25.3 km",
    "totalDuration": "420 min",
    "numberOfStops": 15,
    "numberOfDays": 2,  // Novo campo
    "cost": 123.45
  }
}
```

#### Paleta de Cores por Dia

```javascript
const cores_dias = [
  "#FF6B6B", // Dia 1 - Vermelho
  "#4ECDC4", // Dia 2 - Turquesa
  "#45B7D1", // Dia 3 - Azul
  "#FFA07A", // Dia 4 - Salmão
  "#98D8C8", // Dia 5 - Verde menta
  "#F7DC6F", // Dia 6 - Amarelo
  "#BB8FCE", // Dia 7 - Roxo
  "#85C1E2", // Dia 8 - Azul claro
];
```

As cores se repetem ciclicamente se houver mais de 8 dias.

#### Lógica de Separação por Dia

A API segue a mesma lógica do `main.py` original:

1. **Calcula horários de chegada** considerando tempo de visita (1h) e tempo de viagem
2. **Respeita horários de funcionamento** (startTime - endTime)
3. **Quebra de dia** quando:
   - Horário ultrapassa o `endTime`
   - Nova visita seria após meia-noite
4. **Aguarda abertura** no dia seguinte se necessário

### 2. **Frontend - Service Layer**

#### `/src/services/routeOptimizationService.js`

O método `formatForBestRoute()` foi atualizado para incluir a estrutura de dias:

```javascript
formatForBestRoute(apiResponse) {
  return {
    barsData: [...],     // Lista flat
    days: [...],         // Lista organizada por dia com cores
    routeStats: {
      numberOfDays: apiResponse.stats.numberOfDays  // Novo campo
    }
  }
}
```

### 3. **Frontend - Componente BestRoute**

#### `/src/pages/bestRoute/index.jsx`

##### 3.1. Barra Lateral (Sidebar)

Agora mostra os bares **agrupados por dia** com:

- **Cabeçalho colorido** para cada dia
- **Borda lateral colorida** em cada card de bar
- **Número dentro do dia** (não global)
- **Horário de chegada** exibido

```jsx
<div style={{ backgroundColor: day.color }}>
  📅 Dia {day.dayNumber} - {day.displayDate}
</div>
```

##### 3.2. Mapa

As rotas são desenhadas com **cores diferentes por dia**:

- **Marcadores coloridos**: Cada dia tem marcadores com a cor específica
- **Traços coloridos**: As linhas da rota seguem a cor do dia
- **Múltiplas rotas**: Uma `DirectionsRenderer` por dia

```jsx
{
  directionsPerDay.map((dayRoute, index) => (
    <DirectionsRenderer
      directions={dayRoute.directions}
      options={{
        polylineOptions: {
          strokeColor: dayRoute.color, // Cor específica do dia
          strokeWeight: 5,
        },
      }}
    />
  ));
}
```

##### 3.3. Estatísticas

Adicionado novo campo mostrando número de dias:

```
📍 Paradas: 15 bares
📅 Dias: 2 dias
📏 Distância Total: 25.3 km
```

## 🎨 Visual

### Barra Lateral

```
┌─────────────────────────────────┐
│ 📅 Dia 1 - 15/01/2025           │ ← Vermelho
│    3 bares                      │
└─────────────────────────────────┘
│ 1 │ Alexandre's Bar             │ ← Borda vermelha
│   │ ⭐ 4.5 • 🕐 18:00           │
│ 2 │ Amarelim do Prado          │
│   │ ⭐ 4.3 • 🕐 19:15           │

┌─────────────────────────────────┐
│ 📅 Dia 2 - 16/01/2025           │ ← Turquesa
│    2 bares                      │
└─────────────────────────────────┘
│ 1 │ Bar do Alexandre            │ ← Borda turquesa
│   │ ⭐ 4.7 • 🕐 18:00           │
```

### Mapa

- Marcadores do Dia 1: 🔴 Vermelho
- Linha do Dia 1: ━━━ Vermelho
- Marcadores do Dia 2: 🔵 Turquesa
- Linha do Dia 2: ━━━ Turquesa

## 🔄 Compatibilidade

A implementação mantém **compatibilidade retroativa**:

- Se não houver dados de dias (`days` undefined), usa lista flat
- Marcadores e rotas simples (sem cores) como fallback
- Estatísticas funcionam com ou sem `numberOfDays`

## 🧪 Como Testar

1. **Inicie a API**:

```bash
cd comp-evol-tp1
uv run api.py
```

2. **Inicie o Frontend**:

```bash
cd comp-evol-tp1-frontend
npm run dev
```

3. **Teste com múltiplos dias**:

   - Vá para a página de Filtros
   - Configure:
     - **Data início**: 15/01/2025
     - **Data fim**: 17/01/2025
     - **Horário**: 18:00 - 23:00
   - Clique em "Otimizar Rota"
   - Observe:
     - Bares organizados por dia na sidebar
     - Cores diferentes para cada dia
     - Rotas coloridas no mapa

4. **Teste com um dia único**:
   - Configure mesma data início e fim
   - Veja apenas uma cor

## 📝 Notas Técnicas

### Cálculo de Rotas por Dia

A função `onMapLoad` calcula uma rota do Google Maps **para cada dia**:

```javascript
const directionsPromises = daysByDate.map((day) => {
  return new Promise((resolve) => {
    directionsService.route(
      {
        origin: day.bars[0],
        destination: day.bars[last],
        waypoints: day.bars.slice(1, -1),
      },
      (result) => {
        resolve({
          color: day.color,
          directions: result,
        });
      }
    );
  });
});
```

### Proteção contra Erro de Carregamento

Adicionada verificação `window.google?.maps` antes de renderizar marcadores para evitar erro quando o Google Maps ainda não carregou.

## 🚀 Próximos Passos Possíveis

1. **Legenda de cores** no mapa mostrando qual cor representa qual dia
2. **Filtro por dia** para destacar apenas um dia específico
3. **Animação de transição** entre dias
4. **Exportar roteiro separado por dia** no arquivo de exportação
5. **Tempo estimado por dia** nas estatísticas

---

✅ **Implementação completa e testada!**
