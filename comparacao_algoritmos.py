"""
Script de Comparação: AGM de Kruskal vs Tabu Search

Este script compara a Árvore Geradora Mínima (limite inferior teórico) 
com a solução do Tabu Search para o problema do TSP dos bares.
"""

import pandas as pd
import pickle
from datetime import datetime, timedelta
from utils.kruskal import kruskal, calcular_grau_vertices, visualizar_agm
from utils.tabu_search import tabu_search
from utils.avalia_rota import avaliar_rota


def comparar_algoritmos(df, distancias, tempos, rota_inicial, 
                        hora_inicio, hora_fim, tempo_visita):
    """
    Compara AGM de Kruskal com Tabu Search
    
    Args:
        df: DataFrame com dados dos bares
        distancias: Matriz de distâncias
        tempos: Matriz de tempos
        rota_inicial: Rota inicial para o Tabu Search
        hora_inicio: Horário de início
        hora_fim: Horário de término
        tempo_visita: Tempo de visita em cada bar
    
    Returns:
        dict: Resultados da comparação
    """
    print("=" * 80)
    print("COMPARAÇÃO: AGM de Kruskal vs Tabu Search")
    print("=" * 80)
    
    # 1. Executar Kruskal
    print("\n🌳 Executando Algoritmo de Kruskal para AGM...")
    arestas_agm, custo_agm = kruskal(distancias)
    graus = calcular_grau_vertices(arestas_agm, len(df))
    
    print(f"   ✅ AGM calculada")
    print(f"   📊 Arestas: {len(arestas_agm)}")
    print(f"   💰 Custo total: {custo_agm:.2f}")
    print(f"   📈 Grau médio: {sum(graus)/len(graus):.2f}")
    print(f"   🍃 Folhas (grau 1): {graus.count(1)}")
    
    # 2. Executar Tabu Search
    print("\n🔍 Executando Tabu Search...")
    melhor_rota, custo_tabu = tabu_search(
        rota_inicial, tempos, df, 
        hora_inicio, hora_fim, tempo_visita,
        alpha=1.0, beta=25.0, 
        tabu_tam=15, max_iter=20
    )
    
    print(f"   ✅ Rota otimizada")
    print(f"   📊 Bares visitados: {len(melhor_rota)}")
    print(f"   💰 Custo total: {custo_tabu:.2f}")
    
    # 3. Calcular distância real da rota TSP
    distancia_tabu = 0.0
    for i in range(len(melhor_rota) - 1):
        distancia_tabu += distancias[melhor_rota[i]][melhor_rota[i+1]]
    
    # Adicionar retorno ao ponto inicial (completar ciclo)
    if len(melhor_rota) > 0:
        distancia_tabu += distancias[melhor_rota[-1]][melhor_rota[0]]
    
    print(f"   📏 Distância percorrida: {distancia_tabu:.2f}")
    
    # 4. Análise comparativa
    print("\n" + "=" * 80)
    print("ANÁLISE COMPARATIVA")
    print("=" * 80)
    
    # AGM é limite inferior para TSP
    print(f"\n📊 Custos:")
    print(f"   AGM (limite inferior):  {custo_agm:10.2f}")
    print(f"   Tabu Search (solução):  {custo_tabu:10.2f}")
    print(f"   Distância TSP:          {distancia_tabu:10.2f}")
    
    diferenca_custo = custo_tabu - custo_agm
    percentual_custo = (diferenca_custo / custo_agm * 100) if custo_agm > 0 else 0
    
    diferenca_dist = distancia_tabu - custo_agm
    percentual_dist = (diferenca_dist / custo_agm * 100) if custo_agm > 0 else 0
    
    print(f"\n📈 Diferenças:")
    print(f"   Custo Tabu - Custo AGM:  {diferenca_custo:10.2f} ({percentual_custo:6.2f}% acima)")
    print(f"   Dist. TSP - Custo AGM:   {diferenca_dist:10.2f} ({percentual_dist:6.2f}% acima)")
    
    # Qualidade da solução
    if percentual_custo < 20:
        qualidade = "EXCELENTE ⭐⭐⭐"
    elif percentual_custo < 40:
        qualidade = "BOA ⭐⭐"
    elif percentual_custo < 60:
        qualidade = "RAZOÁVEL ⭐"
    else:
        qualidade = "PODE MELHORAR"
    
    print(f"\n🏆 Qualidade da solução: {qualidade}")
    
    # 5. Análise estrutural
    print(f"\n📐 Análise Estrutural:")
    print(f"   AGM:")
    print(f"      - Conecta todos os {len(df)} bares")
    print(f"      - Usa {len(arestas_agm)} arestas (mínimo para conexão)")
    print(f"      - Não forma ciclos (é uma árvore)")
    print(f"      - Custo mínimo para conectar todos os pontos")
    print(f"\n   TSP (Tabu Search):")
    print(f"      - Visita {len(melhor_rota)} bares")
    print(f"      - Forma um ciclo hamiltoniano")
    print(f"      - Retorna ao ponto inicial")
    print(f"      - Considera restrições de tempo")
    
    # 6. Limite teórico
    print(f"\n🎯 Interpretação:")
    print(f"   A AGM fornece um LIMITE INFERIOR teórico para o TSP.")
    print(f"   Nenhuma solução TSP pode ter custo menor que {custo_agm:.2f}")
    print(f"   O Tabu Search encontrou uma solução {percentual_custo:.2f}% acima deste limite.")
    
    # Resultado
    resultado = {
        'agm': {
            'custo': custo_agm,
            'num_arestas': len(arestas_agm),
            'grau_medio': sum(graus)/len(graus),
            'folhas': graus.count(1),
            'arestas': arestas_agm
        },
        'tabu_search': {
            'custo': custo_tabu,
            'distancia': distancia_tabu,
            'num_bares': len(melhor_rota),
            'rota': melhor_rota
        },
        'comparacao': {
            'diferenca_custo': diferenca_custo,
            'percentual_custo': percentual_custo,
            'diferenca_distancia': diferenca_dist,
            'percentual_distancia': percentual_dist,
            'qualidade': qualidade
        }
    }
    
    return resultado


if __name__ == "__main__":
    # Carregar dados
    print("🔄 Carregando dados...")
    df = pd.read_csv("data/bares.csv")
    
    with open("data/distancias.pkl", "rb") as f:
        distancias, tempos = pickle.load(f)
    
    print(f"✅ {len(df)} bares carregados\n")
    
    # Configurar parâmetros
    data_inicio = datetime(2025, 1, 15).date()
    data_fim = datetime(2025, 1, 15).date()
    hora_inicio = datetime.strptime("18:00", "%H:%M").time()
    hora_fim = datetime.strptime("23:00", "%H:%M").time()
    
    hora_inicio_geral = datetime.combine(data_inicio, hora_inicio)
    hora_fim_geral = datetime.combine(data_fim, hora_fim)
    tempo_visita = timedelta(hours=1)
    
    # Rota inicial (todos os bares)
    rota_inicial = list(range(len(df)))
    
    # Executar comparação
    resultado = comparar_algoritmos(
        df, distancias, tempos, rota_inicial,
        hora_inicio_geral, hora_fim_geral, tempo_visita
    )
    
    # Salvar resultados
    print("\n💾 Salvando resultados...")
    
    # Salvar AGM
    with open("output/agm_kruskal.txt", "w", encoding="utf-8") as f:
        f.write(visualizar_agm(resultado['agm']['arestas'], df))
    
    # Salvar comparação
    with open("output/comparacao_agm_tabu.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("COMPARAÇÃO: AGM de Kruskal vs Tabu Search\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("RESULTADOS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"AGM (Kruskal):\n")
        f.write(f"  Custo total: {resultado['agm']['custo']:.2f}\n")
        f.write(f"  Número de arestas: {resultado['agm']['num_arestas']}\n")
        f.write(f"  Grau médio: {resultado['agm']['grau_medio']:.2f}\n")
        f.write(f"  Vértices folha: {resultado['agm']['folhas']}\n\n")
        
        f.write(f"Tabu Search:\n")
        f.write(f"  Custo total: {resultado['tabu_search']['custo']:.2f}\n")
        f.write(f"  Distância percorrida: {resultado['tabu_search']['distancia']:.2f}\n")
        f.write(f"  Bares visitados: {resultado['tabu_search']['num_bares']}\n\n")
        
        f.write(f"Comparação:\n")
        f.write(f"  Diferença (custo): {resultado['comparacao']['diferenca_custo']:.2f}\n")
        f.write(f"  Percentual acima: {resultado['comparacao']['percentual_custo']:.2f}%\n")
        f.write(f"  Qualidade: {resultado['comparacao']['qualidade']}\n")
    
    print("✅ Resultados salvos em output/")
    print("   - agm_kruskal.txt")
    print("   - comparacao_agm_tabu.txt")
    print("\n✅ Comparação concluída!")
