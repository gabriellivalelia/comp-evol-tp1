import pickle
from datetime import datetime, timedelta

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.tabu_search import tabu_search

app = Flask(__name__)
# Configurar CORS com mais detalhes
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    },
)

# Carregar dados na inicialização
df = pd.read_csv("data/bares.csv")
with open("data/distancias.pkl", "rb") as f:
    distancias, tempos = pickle.load(f)


@app.route("/api/health", methods=["GET"])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify(
        {
            "status": "ok",
            "message": "API de Otimização de Rotas está funcionando",
            "total_bares": len(df),
        }
    )


@app.route("/api/bars", methods=["GET"])
def get_bars():
    """Retorna lista de todos os bares disponíveis"""
    bares_list = []
    for idx, bar in df.iterrows():
        bares_list.append(
            {
                "id": int(idx),
                "name": bar["Nome do Buteco"],
                "rating": float(bar.get("Nota", 4.5)) if "Nota" in bar else 4.5,
            }
        )
    return jsonify(bares_list)


@app.route("/api/test-post", methods=["POST", "OPTIONS"])
def test_post():
    """Endpoint de teste para verificar se POST está funcionando"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.json
        return jsonify(
            {"success": True, "message": "POST funcionou!", "received": data}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/optimize-route", methods=["POST", "OPTIONS"])
def optimize_route():
    """
    Endpoint principal para otimização de rota

    Espera um JSON com:
    {
        "startDate": "2025-11-25",
        "endDate": "2025-11-27",
        "startTime": "16:00",
        "endTime": "23:00",
        "startPoint": "Nome do Bar Inicial",
        "daysOfWeek": ["Segunda", "Terça"],  // opcional
        "minRating": 4.0,  // opcional
        "menuOptions": []  // opcional
    }

    Retorna:
    {
        "bars": [
            {
                "id": 1,
                "name": "Bar do João",
                "address": "Rua X, 123",
                "rating": 4.5,
                "lat": -19.9167,
                "lng": -43.9345,
                "arrivalTime": "16:30",
                "departureTime": "17:30",
                "day": "2025-11-25"
            },
            ...
        ],
        "stats": {
            "totalDistance": "25.5 km",
            "totalDuration": "180 min",
            "numberOfStops": 10,
            "cost": 123.45
        }
    }
    """
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.json
        print("📥 Recebida requisição de otimização")

        if not data:
            return jsonify({"error": "Nenhum dado recebido", "success": False}), 400

        # Validar dados de entrada
        required_fields = ["startDate", "endDate", "startTime", "endTime", "startPoint"]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    {"error": f"Campo obrigatório ausente: {field}", "success": False}
                ), 400

        # Parsear datas e horários
        print("📅 Parseando datas...")
        data_inicio = datetime.strptime(data["startDate"], "%Y-%m-%d").date()
        data_fim = datetime.strptime(data["endDate"], "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(data["startTime"], "%H:%M").time()
        hora_fim = datetime.strptime(data["endTime"], "%H:%M").time()
        print(f"   Período: {data_inicio} a {data_fim}, {hora_inicio} - {hora_fim}")

        # Encontrar o bar inicial
        print("🔍 Buscando bar inicial...")
        nome_bar_inicial = data["startPoint"].strip()

        # Normalizar apóstrofos e outros caracteres Unicode
        # Substituir apóstrofo Unicode (U+2019) por ASCII
        def normalizar_nome(nome):
            """Normaliza nome para comparação, substituindo caracteres Unicode similares"""
            return (
                nome.replace("\u2019", "'")  # ' → '
                .replace("\u2018", "'")  # ' → '
                .replace("\u201c", '"')  # " → "
                .replace("\u201d", '"')  # " → "
                .replace("\u00e9", "e")  # é → e (opcional)
                .replace("\u00e1", "a")  # á → a (opcional)
                .strip()
            )

        nome_bar_inicial_normalizado = normalizar_nome(nome_bar_inicial)
        print(f"   Nome original: '{nome_bar_inicial}'")
        print(f"   Nome normalizado: '{nome_bar_inicial_normalizado}'")

        # Criar coluna temporária com nomes normalizados
        df_temp = df.copy()
        df_temp["Nome_Normalizado"] = df_temp["Nome do Buteco"].apply(normalizar_nome)

        # Buscar usando nome normalizado
        mask = df_temp["Nome_Normalizado"].str.contains(
            nome_bar_inicial_normalizado, case=False, na=False, regex=False
        )
        bares_encontrados = df[mask]
        print(f"   Bares encontrados (busca normalizada): {len(bares_encontrados)}")

        if len(bares_encontrados) == 0:
            # Busca exata com nome normalizado
            mask_exato = df_temp["Nome_Normalizado"] == nome_bar_inicial_normalizado
            bares_encontrados = df[mask_exato]
            print(
                f"   Bares encontrados (busca exata normalizada): {len(bares_encontrados)}"
            )

        if len(bares_encontrados) == 0:
            print(f"❌ Bar não encontrado: '{nome_bar_inicial}'")
            print("   Primeiros 10 bares disponíveis:")
            for i, nome in enumerate(df["Nome do Buteco"].head(10)):
                print(f"      {i}: '{nome}'")
            return jsonify(
                {
                    "error": f'Bar inicial "{nome_bar_inicial}" não encontrado',
                    "success": False,
                }
            ), 404

        bar_inicial_idx = bares_encontrados.index[0]
        print(
            f"✅ Bar inicial encontrado: {df.iloc[bar_inicial_idx]['Nome do Buteco']} (índice: {bar_inicial_idx})"
        )

        # Aplicar filtros (se fornecidos)
        print("🔧 Aplicando filtros...")
        df_filtrado = df.copy()

        # Filtro de nota mínima
        if "minRating" in data and data["minRating"]:
            min_rating = float(data["minRating"])
            print(f"   Nota mínima: {min_rating}")
            if "Nota" in df_filtrado.columns:
                antes = len(df_filtrado)
                df_filtrado = df_filtrado[df_filtrado["Nota"] >= min_rating]
                print(f"   Bares filtrados: {antes} → {len(df_filtrado)}")

        # Criar rota inicial com bar inicial primeiro
        print("📍 Criando rota inicial...")
        indices_filtrados = df_filtrado.index.tolist()
        if bar_inicial_idx not in indices_filtrados:
            indices_filtrados.insert(0, bar_inicial_idx)
        else:
            indices_filtrados.remove(bar_inicial_idx)
            indices_filtrados.insert(0, bar_inicial_idx)

        rota_inicial = indices_filtrados
        print(f"   Total de bares na rota inicial: {len(rota_inicial)}")

        # Configurar período
        print("⚙️ Configurando otimização...")
        hora_inicio_geral = datetime.combine(data_inicio, hora_inicio)
        hora_fim_geral = datetime.combine(data_fim, hora_fim)
        tempo_visita = timedelta(hours=1)

        # Executar otimização
        print("🚀 Executando Tabu Search...")
        alpha, beta = 1.0, 25.0
        melhor_rota, custo = tabu_search(
            rota_inicial,
            tempos,
            df,
            hora_inicio_geral,
            hora_fim_geral,
            tempo_visita,
            alpha=alpha,
            beta=beta,
            tabu_tam=15,
            max_iter=20,
        )
        print(f"✅ Otimização concluída! Custo: {custo:.2f}")
        print(f"   Rota otimizada tem {len(melhor_rota)} bares")

        # Formatar resultado para o frontend
        print("📦 Formatando resultado...")
        bars_result = []
        hora_atual = hora_inicio_geral
        dia_atual = data_inicio
        total_duration = 0
        total_distance_km = 0.0

        for i in range(len(melhor_rota)):
            bar_idx = melhor_rota[i]
            bar = df.iloc[bar_idx]

            # Verificar mudança de dia
            if hora_atual.date() > dia_atual:
                dia_atual = hora_atual.date()

            # Verificar horário de funcionamento
            horario_dia_inicio = datetime.combine(hora_atual.date(), hora_inicio)
            horario_dia_fim = datetime.combine(hora_atual.date(), hora_fim)

            if hora_atual < horario_dia_inicio:
                hora_atual = horario_dia_inicio

            if hora_atual > horario_dia_fim:
                proxima_data = hora_atual.date() + timedelta(days=1)
                if proxima_data <= data_fim:
                    hora_atual = datetime.combine(proxima_data, hora_inicio)
                    dia_atual = proxima_data
                else:
                    break

            # Calcular tempo até próximo bar
            tempo_viagem_minutos = 0
            if i < len(melhor_rota) - 1:
                prox = melhor_rota[i + 1]
                tempo_viagem_minutos = tempos[bar_idx][prox]

            hora_saida = hora_atual + tempo_visita

            # Obter coordenadas (converter formato brasileiro para decimal)
            def converter_coordenada(valor, padrao):
                """
                Converte coordenada de vários formatos para decimal
                Exemplos: '-19.932.821' → -19.932821, '-19,932821' → -19.932821
                """
                try:
                    if isinstance(valor, str):
                        # Contar quantos pontos e vírgulas existem
                        num_pontos = valor.count(".")
                        num_virgulas = valor.count(",")

                        # Se tem mais de um ponto, remover todos (são separadores de milhar)
                        if num_pontos > 1:
                            valor_limpo = valor.replace(".", "")
                            # Adicionar ponto decimal na posição correta (últimos 6 dígitos)
                            # -19932821 → -19.932821
                            if valor_limpo.startswith("-"):
                                valor_limpo = (
                                    valor_limpo[0]
                                    + valor_limpo[1:3]
                                    + "."
                                    + valor_limpo[3:]
                                )
                            else:
                                valor_limpo = valor_limpo[:2] + "." + valor_limpo[2:]
                        # Se tem vírgula, trocar por ponto
                        elif num_virgulas > 0:
                            valor_limpo = valor.replace(",", ".")
                        else:
                            valor_limpo = valor

                        return float(valor_limpo)
                    return float(valor)
                except (ValueError, TypeError) as e:
                    print(
                        f"⚠️  Erro ao converter coordenada '{valor}': {e}. Usando padrão: {padrao}"
                    )
                    return padrao

            lat = converter_coordenada(bar.get("Latitude"), -19.9167)
            lng = converter_coordenada(bar.get("Longitude"), -43.9345)

            bars_result.append(
                {
                    "id": i + 1,
                    "name": bar["Nome do Buteco"],
                    "address": bar.get(
                        "Endereço", f"{bar['Nome do Buteco']}, Belo Horizonte - MG"
                    ),
                    "rating": float(bar.get("Nota", 4.5)),
                    "lat": lat,
                    "lng": lng,
                    "arrivalTime": hora_atual.strftime("%H:%M"),
                    "departureTime": hora_saida.strftime("%H:%M"),
                    "day": hora_atual.strftime("%Y-%m-%d"),
                    "travelTimeToNext": tempo_viagem_minutos,
                }
            )

            if i < len(melhor_rota) - 1:
                tempo_viagem = timedelta(minutes=tempo_viagem_minutos)
                hora_atual += tempo_visita + tempo_viagem
                total_duration += (
                    60 + tempo_viagem_minutos
                )  # 60 min de visita + tempo de viagem
                # Somar distância entre pontos a partir da matriz de distâncias carregada
                try:
                    distancia_km = float(distancias[bar_idx][prox])
                    total_distance_km += distancia_km
                except Exception:
                    # Em caso de problema com índice/matriz, ignorar e continuar
                    pass

            if hora_atual.time() > hora_fim and hora_atual.date() >= data_fim:
                break

        # Organizar bares por dia
        dias_dict = {}
        for bar in bars_result:
            dia = bar["day"]
            if dia not in dias_dict:
                dias_dict[dia] = []
            dias_dict[dia].append(bar)

        # Converter para lista de dias com cores
        cores_dias = [
            "#FF6B6B",  # Vermelho
            "#4ECDC4",  # Turquesa
            "#45B7D1",  # Azul
            "#FFA07A",  # Salmão
            "#98D8C8",  # Verde menta
            "#F7DC6F",  # Amarelo
            "#BB8FCE",  # Roxo
            "#85C1E2",  # Azul claro
        ]

        dias_visitacao = []
        for idx, (dia, bares) in enumerate(sorted(dias_dict.items())):
            dia_obj = datetime.strptime(dia, "%Y-%m-%d").date()
            dias_visitacao.append(
                {
                    "date": dia,
                    "displayDate": dia_obj.strftime("%d/%m/%Y"),
                    "dayNumber": idx + 1,
                    "color": cores_dias[idx % len(cores_dias)],
                    "bars": bares,
                }
            )

        # Preparar estatísticas
        stats = {
            "totalDistance": f"{total_distance_km:.2f} km",
            "totalDuration": f"{total_duration} min",
            "numberOfStops": len(bars_result),
            "numberOfDays": len(dias_visitacao),
            "cost": round(custo, 2),
        }

        print(
            f"✅ Rota otimizada: {len(bars_result)} bares em {len(dias_visitacao)} dias"
        )
        print(f"⏱️  Duração total calculada: {total_duration} min")
        print("📏 Distância total será calculada no frontend com Google Maps")
        return jsonify(
            {
                "bars": bars_result,  # Lista flat para compatibilidade
                "days": dias_visitacao,  # Lista organizada por dias
                "stats": stats,
                "success": True,
            }
        )

    except Exception as e:
        print(f"❌ Erro ao otimizar rota: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/bar-coordinates/<bar_name>", methods=["GET"])
def get_bar_coordinates(bar_name):
    """Retorna coordenadas de um bar específico"""
    mask = df["Nome do Buteco"] == bar_name
    bar = df[mask]

    if len(bar) == 0:
        return jsonify({"error": "Bar não encontrado"}), 404

    bar_data = bar.iloc[0]
    return jsonify(
        {
            "name": bar_data["Nome do Buteco"],
            "lat": float(bar_data.get("Latitude", -19.9167)),
            "lng": float(bar_data.get("Longitude", -43.9345)),
            "address": bar_data.get(
                "Endereço", f"{bar_data['Nome do Buteco']}, Belo Horizonte - MG"
            ),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
