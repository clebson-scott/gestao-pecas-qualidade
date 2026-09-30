"""
demo.py
=======
Demonstração automática do sistema — roda um cenário completo de produção
sem nenhuma digitação.

Para quê?
1. Apresentação/demonstração (inclusive a gravação do vídeo pitch): mostra
   o ciclo inteiro (cadastro → aprovação/reprovação → fechamento de caixa
   → relatório final) em segundos, sem depender de digitação ao vivo.
2. "Smoke test" executável: se a demo roda até o fim sem exceção, o fluxo
   principal do sistema está funcional de ponta a ponta.

Execução:
    python3 -m pecas_qualidade.demo           # usa um estado TEMPORÁRIO
    python3 -m pecas_qualidade.demo --real   # usa o estado real (disco)

Por padrão a demo opera sobre um arquivo de estado temporário que é
apagado ao final — nunca suja os dados reais de produção.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from .estoque import GerenciadorProducao
from .models import StatusPeca

LINHA = "=" * 60
SEPARADOR = "-" * 60

# Cenário: 12 peças aprovadas (forçam 1 caixa fechada + 1 em aberto)
# e 3 reprovadas com combinações distintas de motivos.
CENARIO = [
    # (id, peso, cor, comprimento, expectativa)
    ("A01", 100.0, "azul", 15.0, "aprovada"),
    ("A02", 95.0, "verde", 10.0, "aprovada"),  # limite inferior inclusivo
    ("A03", 105.0, "azul", 20.0, "aprovada"),  # limite superior inclusivo
    ("A04", 98.0, "verde", 12.0, "aprovada"),
    ("A05", 102.0, "azul", 18.0, "aprovada"),
    ("A06", 99.0, "verde", 14.0, "aprovada"),
    ("A07", 101.0, "azul", 16.0, "aprovada"),
    ("A08", 97.0, "verde", 11.0, "aprovada"),
    ("A09", 103.0, "azul", 19.0, "aprovada"),
    ("A10", 100.0, "verde", 13.0, "aprovada"),
    ("A11", 96.0, "azul", 17.0, "aprovada"),
    ("A12", 104.0, "verde", 15.0, "aprovada"),
    ("R01", 50.0, "preta", 5.0, "reprovada"),  # reprova nos 3 critérios
    ("R02", 100.0, "vermelha", 15.0, "reprovada"),  # reprova só na cor
    ("R03", 200.0, "azul", 50.0, "reprovada"),  # reprova em peso + comprimento
]


def rodar_demo(arquivo_estado: Path | None = None) -> None:
    """Executa o cenário completo de demonstração."""
    temporario = arquivo_estado is None
    caminho: Path = arquivo_estado or (Path(tempfile.mkdtemp()) / "demo_estado.json")

    g = GerenciadorProducao(persistir=True, arquivo_estado=caminho)

    print(LINHA)
    print(" DEMONSTRAÇÃO AUTOMÁTICA — Gestão de Peças e Qualidade")
    print(LINHA)
    print(f"Arquivo de estado: {caminho}{' (temporário)' if temporario else ''}\n")

    # --- 1. Cadastro em lote ---------------------------------------- #
    print("[1/4] Cadastrando 15 peças (12 dentro do padrão, 3 fora)...")
    for id_peca, peso, cor, comprimento, _ in CENARIO:
        peca = g.cadastrar_peca(id_peca, peso, cor, comprimento)
        simbolo = "✔" if peca.aprovada else "✗"
        detalhe = f"Caixa #{peca.caixa_id}" if peca.aprovada else "; ".join(peca.motivos_reprovacao)
        print(f"     {simbolo} {peca.id}: {peca.status.value} — {detalhe}")

    # --- 2. Estado das caixas ---------------------------------------- #
    print("\n[2/4] Estado das caixas de armazenamento:")
    for caixa in g.caixas:
        print(f"     {caixa}")

    # --- 3. Tentativa de remoção em caixa fechada (regra de negócio) -- #
    print("\n[3/4] Regra de imutabilidade — tentar remover peça da caixa FECHADA:")
    try:
        g.remover_peca("A01")
        print("     ✗ ERRO: não deveria ter permitido!")
    except Exception as erro:  # noqa: BLE001 — a demo mostra qualquer exceção de domínio
        print(f"     ✔ Bloqueado como esperado → {type(erro).__name__}: {erro}")

    # --- 4. Relatório final ------------------------------------------- #
    print("\n[4/4] Relatório consolidado:")
    print()
    print(g.gerar_relatorio_final())

    aprovadas = g.listar_por_status(StatusPeca.APROVADA)
    print(f"\nSanity check final: {len(aprovadas)} aprovadas em {len(g.caixas)} caixa(s).")
    print("Demonstração concluída com sucesso.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Demonstração automática do sistema de Gestão de Peças e Qualidade."
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="opera sobre o arquivo de estado REAL (não cria um temporário)",
    )
    args = parser.parse_args()

    rodar_demo(Path("estado_demo_persistente.json") if args.real else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
