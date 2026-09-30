"""Testes de integração do menu interativo (main.py).

Testam o sistema "de fora pra dentro", como um usuário real o usaria:
enviam sequências de entradas de teclado e verificam a saída impressa.
Simular o usuário em vez de chamar funções internas diretamente é o que
garante que o menu, as mensagens e o fluxo de erro funcionam de ponta a
ponta — não apenas a lógica de negócio isolada.
"""

import sys
from io import StringIO
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pecas_qualidade import main as cli
from pecas_qualidade.estoque import GerenciadorProducao


@pytest.fixture
def gerenciador(tmp_path):
    return GerenciadorProducao(persistir=False, arquivo_estado=tmp_path / "estado.json")


def simular_cli(entradas: list[str], gerenciador) -> str:
    """Executa o menu principal alimentando `entradas` como teclado e capturando a tela.

    A substituição de `builtins.input` (em vez de um patch complexo de stdin)
    mantém o teste legível: cada item da lista é uma linha digitada pelo
    "usuário", na ordem.
    """
    fila = iter(entradas)
    saida = StringIO()

    def fake_input(_prompt=""):
        try:
            return next(fila)
        except StopIteration as erro:
            raise AssertionError(
                "O programa pediu mais entrada do que o teste forneceu (input esgotado)."
            ) from erro

    import builtins

    original_input, original_print = builtins.input, builtins.print

    def fake_print(*args, **kwargs):
        saida.write(" ".join(str(a) for a in args) + "\n")

    builtins.input, builtins.print = fake_input, fake_print
    try:
        cli.executar(gerenciador)
    finally:
        builtins.input, builtins.print = original_input, original_print
    return saida.getvalue()


def test_menu_simples_cadastro_e_saida(gerenciador):
    saida = simular_cli(["1", "P1", "100", "azul", "15", "", "0"], gerenciador)
    assert "MENU PRINCIPAL" in saida
    assert "Peça APROVADA e armazenada na Caixa #1." in saida
    assert "Encerrando o sistema" in saida


def test_cadastro_peca_reprovada_mostra_todos_os_motivos(gerenciador):
    saida = simular_cli(["1", "P1", "50", "preta", "5", "", "0"], gerenciador)
    assert "REPROVADA" in saida
    assert "peso" in saida
    assert "cor" in saida
    assert "comprimento" in saida


def test_cadastro_duplicado_avisa_sem_quebrar(gerenciador):
    entradas = ["1", "P1", "100", "azul", "15", "", "1", "P1", "100", "azul", "15", "", "0"]
    saida = simular_cli(entradas, gerenciador)
    assert "Já existe uma peça cadastrada com o id 'P1'" in saida


def test_entrada_nao_numerica_repete_pergunta(gerenciador):
    saida = simular_cli(["1", "P1", "abc", "100", "azul", "15", "", "0"], gerenciador)
    assert "Digite um número válido" in saida
    assert "Peça APROVADA" in saida


def test_virgula_decimal_aceita_na_leitura(gerenciador):
    saida = simular_cli(["1", "P1", "98,5", "verde", "12", "", "0"], gerenciador)
    assert "Peça APROVADA" in saida


def test_opcao_invalida_avisa(gerenciador):
    saida = simular_cli(["9", "0"], gerenciador)
    assert "Opção inválida" in saida


def test_listagem_aprovadas(gerenciador):
    saida = simular_cli(["1", "P1", "100", "azul", "15", "", "2", "1", "", "0"], gerenciador)
    assert "PEÇAS APROVADAS (1)" in saida
    assert "Peça #P1" in saida


def test_remocao_de_peca_inexistente_avisa(gerenciador):
    saida = simular_cli(["3", "FANTASMA", "", "0"], gerenciador)
    assert "Nenhuma peça encontrada com o id 'FANTASMA'" in saida


def test_remocao_de_peca_em_caixa_fechada_avisa(gerenciador):
    # 10 peças aprovadas fecham a caixa #1; então tentamos remover a primeira.
    entradas = []
    for i in range(10):
        entradas += ["1", f"P{i}", "100", "azul", "15", ""]
    entradas += ["3", "P0", "", "0"]
    saida = simular_cli(entradas, gerenciador)
    assert "fechada e é imutável" in saida


def test_relatorio_final_e_exportacao(tmp_path, monkeypatch):
    gerenciador = GerenciadorProducao(persistir=False, arquivo_estado=tmp_path / "e.json")
    monkeypatch.chdir(tmp_path)
    saida = simular_cli(["1", "P1", "100", "azul", "15", "", "5", "", "0"], gerenciador)
    assert "RELATÓRIO CONSOLIDADO" in saida
    assert "Total de peças cadastradas ..................... 1" in saida
    assert "relatorio_final.txt" in saida
    exportado = (tmp_path / "relatorio_final.txt").read_text(encoding="utf-8")
    assert "RELATÓRIO CONSOLIDADO" in exportado


def test_listagem_caixas_fechadas_vazia(gerenciador):
    saida = simular_cli(["4", "", "0"], gerenciador)
    assert "nenhuma caixa fechada ainda" in saida


def test_campo_texto_obrigatorio_repete_pergunta(gerenciador):
    saida = simular_cli(["1", "", "P1", "100", "azul", "15", "", "0"], gerenciador)
    assert "Este campo é obrigatório" in saida
    assert "Peça APROVADA" in saida


def test_peso_negativo_rejeitado_pela_leitura(gerenciador):
    saida = simular_cli(["1", "P1", "-5", "100", "azul", "15", "", "0"], gerenciador)
    assert "maior ou igual a 0" in saida


def test_cor_invalida_avisa_sem_quebrar(gerenciador):
    saida = simular_cli(["1", "P1", "100", "roxo-que-não-existe", "15", "", "0"], gerenciador)
    assert "não reconhecida" in saida
    assert "Cores aceitas" in saida


def test_listagem_reprovadas(gerenciador):
    saida = simular_cli(["1", "P1", "50", "preta", "5", "", "2", "2", "", "0"], gerenciador)
    assert "PEÇAS REPROVADAS (1)" in saida


def test_listagem_todas(gerenciador):
    saida = simular_cli(["1", "P1", "100", "azul", "15", "", "2", "9", "", "0"], gerenciador)
    assert "TODAS AS PEÇAS (1)" in saida


def test_remover_peca_aprovada_em_caixa_aberta_via_menu(gerenciador):
    saida = simular_cli(
        ["1", "P1", "100", "azul", "15", "", "3", "P1", "", "2", "3", "", "0"],
        gerenciador,
    )
    assert "Peça removida" in saida
    assert "TODAS AS PEÇAS (0)" in saida
