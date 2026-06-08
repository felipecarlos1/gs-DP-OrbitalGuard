"""
=============================================================
OrbitalGuard — Dynamic Programming
Global Solution 2026 | FIAP | Space Connect

Problema:
    Dado um evento de desastre detectado por satélite (ex: queimada,
    enchente), qual é o caminho de menor latência para o alerta chegar
    até o centro de resposta responsável pela região afetada, trafegando
    pela rede de comunicação orbital (satélites + estações terrestres)?

Solução:
    Modelamos a rede orbital como um grafo ponderado e aplicamos o
    algoritmo de Dijkstra para encontrar o caminho ótimo (menor
    latência total em milissegundos).
=============================================================
"""

import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# =============================================================
# 1. DEFINIÇÃO DO GRAFO
#    Nós: satélites (SAT), estações terrestres (EST) e
#         centros de resposta (CR).
#    Arestas: (nó_origem, nó_destino, latência_ms)
# =============================================================

def criar_rede_orbital():
    """
    Cria e retorna o grafo da rede orbital do OrbitalGuard.

    A rede possui:
      - 15 satélites em órbita baixa (LEO)
      - 10 estações terrestres de retransmissão
      -  8 centros de resposta a desastres

    Total: 33 nós e mais de 30 arestas bidirecionais.

    Retorna:
        grafo (dict): dicionário de adjacência {nó: [(vizinho, peso), ...]}
        posicoes (dict): coordenadas (x, y) para plotagem
        tipos (dict): tipo de cada nó para colorização
    """

    # --- Nós ---
    nos = [
        # Satélites LEO
        "SAT-01", "SAT-02", "SAT-03", "SAT-04", "SAT-05",
        "SAT-06", "SAT-07", "SAT-08", "SAT-09", "SAT-10",
        "SAT-11", "SAT-12", "SAT-13", "SAT-14", "SAT-15",
        # Estações terrestres
        "EST-Manaus",    "EST-Belem",     "EST-Recife",
        "EST-Salvador",  "EST-Brasilia",  "EST-RioDeJaneiro",
        "EST-SaoPaulo",  "EST-Curitiba",  "EST-PortoAlegre",
        "EST-CampoGrande",
        # Centros de resposta
        "CR-Norte",      "CR-Nordeste",   "CR-CentroOeste",
        "CR-Sudeste",    "CR-Sul",        "CR-Amazonia",
        "CR-Pantanal",   "CR-Cerrado",
    ]

    # --- Tipos para colorização ---
    tipos = {}
    for n in nos:
        if n.startswith("SAT"):
            tipos[n] = "satelite"
        elif n.startswith("EST"):
            tipos[n] = "estacao"
        else:
            tipos[n] = "centro"

    # --- Arestas (origem, destino, latência em ms) ---
    # Latência orbital entre satélites: 20-80 ms
    # Satélite → Estação (downlink): 30-100 ms
    # Estação → Centro de resposta: 5-20 ms
    arestas = [
        # Malha inter-satelital
        ("SAT-01", "SAT-02",  25), ("SAT-02", "SAT-03",  30),
        ("SAT-03", "SAT-04",  22), ("SAT-04", "SAT-05",  28),
        ("SAT-05", "SAT-06",  35), ("SAT-06", "SAT-07",  40),
        ("SAT-07", "SAT-08",  20), ("SAT-08", "SAT-09",  33),
        ("SAT-09", "SAT-10",  27), ("SAT-10", "SAT-11",  45),
        ("SAT-11", "SAT-12",  38), ("SAT-12", "SAT-13",  29),
        ("SAT-13", "SAT-14",  55), ("SAT-14", "SAT-15",  42),
        ("SAT-15", "SAT-01",  60), ("SAT-01", "SAT-06",  50),
        ("SAT-03", "SAT-09",  48), ("SAT-05", "SAT-12",  37),
        ("SAT-07", "SAT-14",  65), ("SAT-02", "SAT-10",  44),
        # Downlinks satélite → estação
        ("SAT-01", "EST-Manaus",       45), ("SAT-02", "EST-Belem",        50),
        ("SAT-03", "EST-Recife",       55), ("SAT-04", "EST-Salvador",     48),
        ("SAT-05", "EST-Brasilia",     40), ("SAT-06", "EST-RioDeJaneiro", 52),
        ("SAT-07", "EST-SaoPaulo",     38), ("SAT-08", "EST-Curitiba",     43),
        ("SAT-09", "EST-PortoAlegre",  47), ("SAT-10", "EST-CampoGrande",  41),
        ("SAT-11", "EST-Manaus",       60), ("SAT-12", "EST-Brasilia",     35),
        ("SAT-13", "EST-SaoPaulo",     42), ("SAT-14", "EST-Recife",       58),
        ("SAT-15", "EST-Salvador",     53),
        # Estação → Centro de resposta
        ("EST-Manaus",       "CR-Norte",       8),
        ("EST-Belem",        "CR-Norte",      10),
        ("EST-Recife",       "CR-Nordeste",    7),
        ("EST-Salvador",     "CR-Nordeste",    9),
        ("EST-Brasilia",     "CR-CentroOeste", 6),
        ("EST-CampoGrande",  "CR-CentroOeste", 8),
        ("EST-RioDeJaneiro", "CR-Sudeste",     5),
        ("EST-SaoPaulo",     "CR-Sudeste",     6),
        ("EST-Curitiba",     "CR-Sul",         7),
        ("EST-PortoAlegre",  "CR-Sul",         9),
        ("EST-Manaus",       "CR-Amazonia",    6),
        ("EST-CampoGrande",  "CR-Pantanal",    8),
        ("EST-Brasilia",     "CR-Cerrado",     7),
        ("EST-SaoPaulo",     "CR-Cerrado",    11),
    ]

    # --- Monta dicionário de adjacência (grafo não-dirigido) ---
    grafo = {n: [] for n in nos}
    for origem, destino, peso in arestas:
        grafo[origem].append((destino, peso))
        grafo[destino].append((origem, peso))

    # --- Posições para o layout do plot ---
    posicoes = {
        # Satélites — duas linhas orbitais
        "SAT-01": (1, 9),  "SAT-02": (2, 9),  "SAT-03": (3, 9),
        "SAT-04": (4, 9),  "SAT-05": (5, 9),  "SAT-06": (6, 9),
        "SAT-07": (7, 9),  "SAT-08": (8, 9),  "SAT-09": (9, 9),
        "SAT-10": (10, 9), "SAT-11": (2, 7),  "SAT-12": (4, 7),
        "SAT-13": (6, 7),  "SAT-14": (8, 7),  "SAT-15": (10, 7),
        # Estações — faixa intermediária
        "EST-Manaus":       (1, 5),  "EST-Belem":        (2.5, 5),
        "EST-Recife":       (4, 5),  "EST-Salvador":     (5.5, 5),
        "EST-Brasilia":     (7, 5),  "EST-RioDeJaneiro": (8, 5),
        "EST-SaoPaulo":     (9, 5),  "EST-Curitiba":     (10, 5),
        "EST-PortoAlegre":  (11, 5), "EST-CampoGrande":  (6, 5),
        # Centros — linha inferior
        "CR-Norte":       (1.5, 2), "CR-Nordeste":    (4, 2),
        "CR-CentroOeste": (6.5, 2), "CR-Sudeste":     (8.5, 2),
        "CR-Sul":         (10.5, 2),"CR-Amazonia":    (2.5, 2),
        "CR-Pantanal":    (5.5, 2), "CR-Cerrado":     (7.5, 2),
    }

    return grafo, posicoes, tipos, arestas


# =============================================================
# 2. ALGORITMO DE DIJKSTRA
# =============================================================

def dijkstra(grafo, origem):
    """
    Executa o algoritmo de Dijkstra a partir de um nó de origem.

    Parâmetros:
        grafo (dict): dicionário de adjacência {nó: [(vizinho, peso), ...]}
        origem (str): nó inicial (satélite que detectou o evento)

    Retorna:
        distancias (dict): menor latência acumulada até cada nó
        predecessores (dict): nó anterior no caminho ótimo
    """
    distancias   = {no: float('inf') for no in grafo}
    predecessores = {no: None for no in grafo}
    distancias[origem] = 0

    # Fila de prioridade: (latência_acumulada, nó)
    fila = [(0, origem)]

    while fila:
        latencia_atual, no_atual = heapq.heappop(fila)

        # Ignora entradas obsoletas na fila
        if latencia_atual > distancias[no_atual]:
            continue

        for vizinho, peso in grafo[no_atual]:
            nova_latencia = latencia_atual + peso
            if nova_latencia < distancias[vizinho]:
                distancias[vizinho]    = nova_latencia
                predecessores[vizinho] = no_atual
                heapq.heappush(fila, (nova_latencia, vizinho))

    return distancias, predecessores


def reconstruir_caminho(predecessores, destino):
    """
    Reconstrói o caminho ótimo do destino até a origem,
    seguindo os predecessores de trás para frente.

    Parâmetros:
        predecessores (dict): saída de dijkstra()
        destino (str): nó final

    Retorna:
        caminho (list): lista de nós do início ao fim
    """
    caminho = []
    no = destino
    while no is not None:
        caminho.append(no)
        no = predecessores[no]
    caminho.reverse()
    return caminho


# =============================================================
# 3. PLOTAGEM DO GRAFO
# =============================================================

def plotar_grafo(grafo, posicoes, tipos, arestas, caminho_destaque=None):
    """
    Plota o grafo da rede orbital com destaque opcional
    para o caminho ótimo encontrado pelo Dijkstra.

    Parâmetros:
        grafo (dict): dicionário de adjacência
        posicoes (dict): coordenadas de cada nó
        tipos (dict): tipo de cada nó (satelite/estacao/centro)
        arestas (list): lista de (origem, destino, peso)
        caminho_destaque (list): caminho a destacar em laranja
    """
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_facecolor("#0d1117")
    fig.patch.set_facecolor("#0d1117")

    cores_no = {
        "satelite": "#4dabf7",
        "estacao":  "#69db7c",
        "centro":   "#ffa94d",
    }

    # Conjunto de arestas do caminho ótimo para destaque
    arestas_caminho = set()
    if caminho_destaque and len(caminho_destaque) > 1:
        for i in range(len(caminho_destaque) - 1):
            a, b = caminho_destaque[i], caminho_destaque[i + 1]
            arestas_caminho.add((a, b))
            arestas_caminho.add((b, a))

    # --- Desenha arestas ---
    for origem, destino, peso in arestas:
        x0, y0 = posicoes[origem]
        x1, y1 = posicoes[destino]
        destaque = (origem, destino) in arestas_caminho
        cor   = "#ff6b35" if destaque else "#30363d"
        lw    = 2.5       if destaque else 0.8
        alpha = 1.0       if destaque else 0.6
        ax.plot([x0, x1], [y0, y1], color=cor, linewidth=lw, alpha=alpha, zorder=1)
        # Rótulo de peso nas arestas do caminho
        if destaque:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            ax.text(mx, my, f"{peso}ms", fontsize=7, color="#ff6b35",
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", fc="#0d1117", ec="none"))

    # --- Desenha nós ---
    for no, (x, y) in posicoes.items():
        tipo = tipos[no]
        cor  = cores_no[tipo]
        no_em_caminho = caminho_destaque and no in caminho_destaque

        tamanho = 220 if no_em_caminho else 120
        borda   = "#ffffff" if no_em_caminho else cor
        ax.scatter(x, y, s=tamanho, color=cor, edgecolors=borda,
                   linewidths=1.5, zorder=3)
        ax.text(x, y - 0.35, no, fontsize=6.5, color="#e6edf3",
                ha="center", va="top", zorder=4)

    # --- Camadas / faixas ---
    for y, label, cor_faixa in [
        (8.2, "Órbita LEO — Satélites",         "#161b22"),
        (4.2, "Estações Terrestres",             "#0d1117"),
        (1.2, "Centros de Resposta a Desastres", "#161b22"),
    ]:
        ax.axhspan(y, y + 1.5, color=cor_faixa, alpha=0.4, zorder=0)
        ax.text(0.3, y + 0.7, label, fontsize=8, color="#8b949e",
                style="italic", va="center")

    # --- Legenda ---
    legenda = [
        mpatches.Patch(color="#4dabf7", label="Satélite LEO"),
        mpatches.Patch(color="#69db7c", label="Estação Terrestre"),
        mpatches.Patch(color="#ffa94d", label="Centro de Resposta"),
        mpatches.Patch(color="#ff6b35", label="Caminho Ótimo (Dijkstra)"),
    ]
    ax.legend(handles=legenda, loc="upper right", fontsize=8,
              facecolor="#161b22", edgecolor="#30363d", labelcolor="#e6edf3")

    ax.set_title("OrbitalGuard — Rede Orbital de Alertas de Desastre",
                 fontsize=13, color="#e6edf3", pad=12)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("/mnt/user-data/outputs/orbitalguard_grafo.png",
                dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.show()
    print("Grafo salvo em orbitalguard_grafo.png")


# =============================================================
# 4. EXECUÇÃO PRINCIPAL
# =============================================================

def main():
    """
    Fluxo principal do OrbitalGuard:
      1. Cria a rede orbital
      2. Define o evento (satélite de origem) e o destino (centro de resposta)
      3. Executa Dijkstra
      4. Exibe o caminho ótimo e a latência total
      5. Plota o grafo com o caminho destacado
    """
    print("=" * 60)
    print("  OrbitalGuard — Roteamento de Alertas via Rede Orbital")
    print("=" * 60)

    # Cria a rede
    grafo, posicoes, tipos, arestas = criar_rede_orbital()

    # Cenário: SAT-03 detectou uma queimada no Nordeste
    origem  = "SAT-03"
    destino = "CR-Nordeste"

    print(f"\n[EVENTO DETECTADO]")
    print(f"  Satélite sensor : {origem}")
    print(f"  Centro de destino: {destino}")
    print(f"  Objetivo: encontrar rota de menor latência\n")

    # Executa Dijkstra
    distancias, predecessores = dijkstra(grafo, origem)

    # Reconstrói caminho ótimo
    caminho = reconstruir_caminho(predecessores, destino)
    latencia_total = distancias[destino]

    # Exibe resultado
    print("[CAMINHO ÓTIMO ENCONTRADO — DIJKSTRA]")
    print("  " + " → ".join(caminho))
    print(f"\n  Latência total: {latencia_total} ms")

    print("\n[TOP 5 — MENORES LATÊNCIAS ATÉ CENTROS DE RESPOSTA]")
    centros = {k: v for k, v in distancias.items() if k.startswith("CR-")}
    for i, (cr, lat) in enumerate(sorted(centros.items(), key=lambda x: x[1])[:5], 1):
        print(f"  {i}. {cr:25s} → {lat} ms")

    print("\n[DETALHAMENTO DO CAMINHO ÓTIMO]")
    latencia_acum = 0
    for i in range(len(caminho) - 1):
        a, b = caminho[i], caminho[i + 1]
        peso = next(p for (v, p) in grafo[a] if v == b)
        latencia_acum += peso
        print(f"  {a:25s} → {b:25s}  (+{peso:3d} ms)  acumulado: {latencia_acum} ms")

    # Plota o grafo
    plotar_grafo(grafo, posicoes, tipos, arestas, caminho_destaque=caminho)

    print("\n[CONCLUSÃO]")
    print(f"  O alerta gerado por {origem} chegou a {destino}")
    print(f"  em {latencia_total} ms pelo caminho ótimo de {len(caminho)-1} saltos.")
    print("=" * 60)


if __name__ == "__main__":
    main()
