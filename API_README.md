# API de Otimização de Rotas - Comida di Buteco

API Flask para otimizar rotas entre bares do Comida di Buteco usando algoritmo Tabu Search.

## 🚀 Instalação

### 1. Instalar dependências

```bash
cd comp-evol-tp1
uv sync
```

### 2. Ativar ambiente virtual

```bash
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 3. Instalar dependências adicionais da API

```bash
uv add flask flask-cors
```

## 📡 Executar a API

```bash
python api.py
```

A API estará disponível em `http://localhost:5000`

## 🔌 Endpoints

### 1. Health Check

**GET** `/api/health`

Verifica se a API está funcionando.

**Resposta:**

```json
{
  "status": "ok",
  "message": "API de Otimização de Rotas está funcionando",
  "total_bares": 124
}
```

### 2. Listar Bares

**GET** `/api/bars`

Retorna lista de todos os bares disponíveis.

**Resposta:**

```json
[
  {
    "id": 0,
    "name": "Alexandre's Bar",
    "rating": 4.5
  },
  ...
]
```

### 3. Otimizar Rota

**POST** `/api/optimize-route`

Otimiza a rota entre bares com base nos filtros fornecidos.

**Request Body:**

```json
{
  "startDate": "2025-11-25",
  "endDate": "2025-11-27",
  "startTime": "16:00",
  "endTime": "23:00",
  "startPoint": "Alexandre's Bar",
  "daysOfWeek": ["Segunda", "Terça"],
  "minRating": 4.0,
  "menuOptions": ["Carne", "Frango"]
}
```

**Resposta:**

```json
{
  "bars": [
    {
      "id": 1,
      "name": "Alexandre's Bar",
      "address": "R. David Alves do Valê, 68 - Santa Rosa",
      "rating": 4.5,
      "lat": -19.8618937,
      "lng": -43.9443309,
      "arrivalTime": "16:00",
      "departureTime": "17:00",
      "day": "2025-11-25",
      "travelTimeToNext": 15
    },
    ...
  ],
  "stats": {
    "totalDistance": "25.5 km",
    "totalDuration": "180 min",
    "numberOfStops": 10,
    "cost": 123.45
  },
  "success": true
}
```

### 4. Buscar Coordenadas de Bar

**GET** `/api/bar-coordinates/<bar_name>`

Retorna coordenadas de um bar específico.

**Resposta:**

```json
{
  "name": "Alexandre's Bar",
  "lat": -19.8618937,
  "lng": -43.9443309,
  "address": "R. David Alves do Valê, 68 - Santa Rosa"
}
```

## 🔧 Configuração do Frontend

### 1. Configurar variável de ambiente

Crie ou edite o arquivo `.env` no diretório do frontend:

```env
VITE_API_BASE_URL=http://localhost:5000
```

### 2. O serviço já está integrado

O serviço `routeOptimizationService.js` já está configurado e sendo usado pela página de filtros.

## 📊 Algoritmo de Otimização

A API utiliza o algoritmo **Tabu Search** implementado em `utils/tabu_search.py` para:

1. Otimizar a ordem de visita aos bares
2. Considerar horários de funcionamento
3. Minimizar distância e tempo de viagem
4. Respeitar o período de viagem (múltiplos dias)
5. Aplicar filtros de nota mínima e preferências

## 🐛 Troubleshooting

### Erro: "API não está disponível"

- Verifique se a API está rodando: `python api.py`
- Verifique se a porta 5000 está disponível
- Verifique CORS se estiver em produção

### Erro: "Bar inicial não encontrado"

- Verifique se o nome do bar está correto no CSV
- Use o endpoint `/api/bars` para ver a lista de bares disponíveis

### Erro ao carregar dados

- Verifique se existe `data/bares.csv`
- Verifique se existe `data/distancias.pkl`

## 📝 Formato dos Dados

### bares.csv

Deve conter colunas:

- `Nome do Buteco`: Nome do bar
- `Nota`: Avaliação (opcional, padrão 4.5)
- `Latitude`: Latitude do bar
- `Longitude`: Longitude do bar
- `Endereço`: Endereço completo (opcional)

### distancias.pkl

Arquivo pickle contendo tupla `(distancias, tempos)`:

- `distancias`: Matriz NxN de distâncias em metros
- `tempos`: Matriz NxN de tempos em minutos

## 🎯 Próximos Passos

- [ ] Adicionar autenticação
- [ ] Implementar cache de rotas
- [ ] Adicionar mais algoritmos de otimização
- [ ] Deploy em produção
