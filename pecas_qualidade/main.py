#!/usr/bin/env python3
"""
main.py
=======
Interface de linha de comando (CLI) do sistema de Gestão de Peças,
Qualidade e Armazenamento.

Este módulo é a ÚNICA parte do sistema que conversa com o terminal
(``input``/``print``). Toda a lógica de negócio vive em ``estoque.py``,
``regras.py`` e ``models.py`` — isso é o padrão de projeto conhecido como
"separação entre interface e domínio": o mesmo ``GerenciadorProducao``
usado aqui poderia, no futuro, ser plugado numa API web ou numa interface
gráfica sem que uma linha das regras de negócio precisasse mudar.

Execução:
    python3 -m pecas_qualidade.main
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Permite executar tanto como módulo (`python -m pecas_qualidade.main`)
# quanto diretamente (`python3 main.py`) de dentro da pasta do pacote.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from pecas_qualidade.estoque import GerenciadorProducao, RelatorioFinal
    from pecas_qualidade.excecoes import (
        ErroDominioPecas,
        PecaDuplicadaError,
        PecaNaoEncontradaError,
        RemocaoBloqueadaError,
    )
    from pecas_qualidade.models import StatusPeca
else:
    from .estoque import GerenciadorProducao, RelatorioFinal
    from .excecoes import (
        ErroDominioPecas,
        PecaDuplicadaError,
        PecaNaoEncontradaError,
        RemocaoBloqueadaError,
    )
    from .models import StatusPeca

LOG_ARQUIVO = Path(__file__).resolve().parent / "pecas.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_ARQUIVO, encoding="utf-8")],
)

TITULO_ARTE = r"""
   ____                 _  __        ___          _ _     _           _
  / ___| _____  __ __ _| |/ /  __ _ / _ \ _   _  __ _| (_) __| | __ _  __| | ___
 | |  _ / _ \ \/ // _` |   <  / _` | | | | | | |/ _` | | |/ _` |/ _` |/ _` |/ _ \
 | |_| |  __/>  <| (_| | . \| (_| | |_| | |_| | (_| | | | (_| | (_| | (_| |  __/
  \____|\___/_/\_\\__,_|_|\_\\__,_|\___/ \__,_|\__,_|_|_|\__,_|\__,_|\__,_|\___|

        Sistema de Gestão de Peças, Qualidade e Armazenamento
"""

LARGURA_MENU = 56


def limpar_tela_logica() -> None:
    """Imprime uma quebra visual entre telas (sem depender de os.system)."""
    print("\n" * 1)


def pausar() -> None:
    """Aguarda o usuário confirmar antes de voltar ao menu."""
    input("\nPressione ENTER para continuar...")


def ler_texto(mensagem: str, obrigatorio: bool = True) -> str:
    """Lê uma string do usuário, repetindo a pergunta enquanto for inválida.

    Args:
        mensagem: prompt exibido ao usuário.
        obrigatorio: se ``True``, não aceita resposta vazia.
    """
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print("  ⚠ Este campo é obrigatório. Tente novamente.")


def ler_float(mensagem: str, minimo: float | None = None, maximo: float | None = None) -> float:
    """Lê um número decimal do usuário, validando o formato e a faixa opcional.

    Repete a pergunta em caso de entrada inválida (texto não numérico) em
    vez de deixar o programa quebrar com ``ValueError`` — um requisito
    básico de robustez para qualquer sistema que recebe dados manuais de
    um operador de produção.
    """
    while True:
        bruto = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(bruto)
        except ValueError:
            print("  ⚠ Digite um número válido (ex.: 98.5).")
            continue
        if minimo is not None and valor < minimo:
            print(f"  ⚠ O valor deve ser maior ou igual a {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"  ⚠ O valor deve ser menor ou igual a {maximo}.")
            continue
        return valor


def exibir_menu() -> str:
    print("\n" + "=" * LARGURA_MENU)
    print(" MENU PRINCIPAL".center(LARGURA_MENU))
    print("=" * LARGURA_MENU)
    print(" 1. Cadastrar nova peça")
    print(" 2. Listar peças aprovadas/reprovadas")
    print(" 3. Remover peça cadastrada")
    print(" 4. Listar caixas fechadas")
    print(" 5. Gerar relatório final")
    print(" 0. Sair")
    print("=" * LARGURA_MENU)
    return input(" Escolha uma opção: ").strip()


def acao_cadastrar_peca(gerenciador: GerenciadorProducao) -> None:
    print("\n--- Cadastro de nova peça ---")
    id_peca = ler_texto("ID da peça: ")
    peso = ler_float("Peso (g): ", minimo=0)
    cor = ler_texto("Cor (ex.: azul, verde, vermelha...): ")
    comprimento = ler_float("Comprimento (cm): ", minimo=0)

    try:
        peca = gerenciador.cadastrar_peca(id_peca=id_peca, peso=peso, cor=cor, comprimento=comprimento)
    except PecaDuplicadaError as erro:
        print(f"  ✗ {erro}")
        return
    except ValueError as erro:
        print(f"  ✗ {erro}")
        return

    if peca.aprovada:
        print(f"  ✔ Peça APROVADA e armazenada na Caixa #{peca.caixa_id}.")
    else:
        print(f"  ✗ Peça REPROVADA. Motivo(s): {', '.join(peca.motivos_reprovacao)}.")


def acao_listar_pecas(gerenciador: GerenciadorProducao) -> None:
    print("\n--- Listagem de peças ---")
    print(" 1. Ver aprovadas")
    print(" 2. Ver reprovadas")
    print(" 3. Ver todas")
    escolha = input(" Escolha uma opção: ").strip()

    if escolha == "1":
        pecas = gerenciador.listar_por_status(StatusPeca.APROVADA)
        titulo = "PEÇAS APROVADAS"
    elif escolha == "2":
        pecas = gerenciador.listar_por_status(StatusPeca.REPROVADA)
        titulo = "PEÇAS REPROVADAS"
    else:
        pecas = list(gerenciador.pecas.values())
        titulo = "TODAS AS PEÇAS"

    print(f"\n{titulo} ({len(pecas)}):")
    if not pecas:
        print("  (nenhuma peça encontrada)")
    for peca in pecas:
        print(f"  {peca}")


def acao_remover_peca(gerenciador: GerenciadorProducao) -> None:
    print("\n--- Remoção de peça ---")
    id_peca = ler_texto("ID da peça a remover: ")
    try:
        peca = gerenciador.remover_peca(id_peca)
    except PecaNaoEncontradaError as erro:
        print(f"  ✗ {erro}")
        return
    except RemocaoBloqueadaError as erro:
        print(f"  ✗ {erro}")
        return
    print(f"  ✔ Peça removida: {peca}")


def acao_listar_caixas_fechadas(gerenciador: GerenciadorProducao) -> None:
    print("\n--- Caixas fechadas ---")
    caixas = gerenciador.listar_caixas_fechadas()
    if not caixas:
        print("  (nenhuma caixa fechada ainda)")
    for caixa in caixas:
        print(f"  {caixa} — peças: {', '.join(caixa.pecas_ids)}")


def acao_gerar_relatorio(gerenciador: GerenciadorProducao) -> RelatorioFinal:
    print()
    relatorio = gerenciador.gerar_relatorio_final()
    print(relatorio)
    return relatorio


def salvar_relatorio_em_arquivo(relatorio: RelatorioFinal, caminho: Path) -> None:
    """Exporta o relatório final para um arquivo .txt, além de exibi-lo na tela.

    Esse é um dos itens de "vá além": o relatório não fica preso ao
    terminal, podendo ser anexado a um e-mail, sistema de qualidade ou
    auditoria posterior.
    """
    caminho.write_text(str(relatorio) + "\n", encoding="utf-8")


def executar() -> None:
    print(TITULO_ARTE)
    gerenciador = GerenciadorProducao()
    print(
        f"Estado carregado: {len(gerenciador.pecas)} peça(s), "
        f"{len(gerenciador.caixas)} caixa(s)."
    )

    acoes = {
        "1": acao_cadastrar_peca,
        "2": acao_listar_pecas,
        "3": acao_remover_peca,
        "4": acao_listar_caixas_fechadas,
    }

    while True:
        opcao = exibir_menu()

        if opcao == "0":
            print("\nEncerrando o sistema. Estado salvo em disco. Até logo!")
            break

        if opcao == "5":
            relatorio = acao_gerar_relatorio(gerenciador)
            caminho_export = Path(__file__).resolve().parent / "relatorio_final.txt"
            salvar_relatorio_em_arquivo(relatorio, caminho_export)
            print(f"\n(Relatório também exportado para: {caminho_export})")
            pausar()
            continue

        acao = acoes.get(opcao)
        if acao is None:
            print("  ⚠ Opção inválida. Escolha um número entre 0 e 5.")
            continue

        try:
            acao(gerenciador)
        except ErroDominioPecas as erro:
            # Rede de segurança final: qualquer regra de negócio violada
            # que não tenha sido tratada especificamente na ação é
            # capturada aqui, sem derrubar o programa.
            print(f"  ✗ Erro: {erro}")
        pausar()


if __name__ == "__main__":
    try:
        executar()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário (Ctrl+C). Estado salvo em disco. Até logo!")
