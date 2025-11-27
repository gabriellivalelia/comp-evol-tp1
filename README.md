# Comida di Buteco - Backend

Backend da plataforma Comida di Buteco - Sistema de otimização de rotas para tour gastronômico em Belo Horizonte.

## 📋 Pré-requisitos

### 1. Instalar uv (Gerenciador de Pacotes Python)

**uv** é um gerenciador de pacotes Python extremamente rápido, escrito em Rust.

#### Linux/macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell):

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Documentação oficial**: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

### 2. Instalar Python 3.10+

Recomenda-se Python 3.10 ou superior. Veja: [https://www.python.org/downloads/](https://www.python.org/downloads/)

## 🚀 Início Rápido

### Passo a Passo Completo

#### 1. Clone o repositório

```bash
git clone https://github.com/gabriellivalelia/comp-evol-tp1
cd comp-evol-tp1
```

#### 2. Instalar dependências

```bash
uv sync
```

#### 3. Configurar variáveis de ambiente (opcional)

O backend não exige variáveis obrigatórias para rodar localmente, mas você pode configurar caminhos de dados ou portas editando diretamente o código ou usando variáveis de ambiente.

#### 4. Iniciar o servidor

```bash
uv run api.py
```

O servidor estará disponível em: `http://localhost:5000`

## 📝 Comandos Disponíveis

```bash
uv run api.py          # Inicia o servidor Flask em modo desenvolvimento
```

## 🗄️ Dados Utilizados

Os dados dos bares e matrizes de distância/tempo estão na pasta `data/`:

- `data/bares.csv` — Lista de bares participantes
- `data/distancias.pkl` — Matrizes de distância e tempo
- Outros arquivos auxiliares para análise

## 📖 Links Úteis

- **Documentação do uv**: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- **Documentação do Flask**: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- **Documentação do pandas**: [https://pandas.pydata.org/](https://pandas.pydata.org/)

## 👥 Autores

- Gabrielli Valelia Sousa da Silva
- Júlia Diniz Rodrigues

---

Este projeto é parte do trabalho acadêmico da disciplina de Computação Evolucionária - UFMG 2025.2
