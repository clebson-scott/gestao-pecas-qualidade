"""Testes unitários para a classe GerenciadorProducao (estoque.py)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pecas_qualidade.estoque import GerenciadorProducao
from pecas_qualidade.excecoes import (
    PecaDuplicadaError,
    PecaNaoEncontradaError,
    RemocaoBloqueadaError,
)
from pecas_qualidade.models import StatusPeca


@pytest.fixture
def gerenciador(tmp_path):
    """Gerenciador sem persistência em disco, isolado por teste."""
    return GerenciadorProducao(persistir=False, arquivo_estado=tmp_path / "estado_teste.json")


def test_cadastrar_peca_aprovada(gerenciador):
    peca = gerenciador.cadastrar_peca("P1", peso=100, cor="azul", comprimento=15)
    assert peca.aprovada is True
    assert peca.caixa_id == 1


def test_cadastrar_peca_reprovada_nao_entra_em_caixa(gerenciador):
    peca = gerenciador.cadastrar_peca("P1", peso=50, cor="preta", comprimento=5)
    assert peca.aprovada is False
    assert peca.caixa_id is None
    assert gerenciador.listar_caixas_abertas() == []


def test_cadastro_duplicado_levanta_erro(gerenciador):
    gerenciador.cadastrar_peca("P1", peso=100, cor="azul", comprimento=15)
    with pytest.raises(PecaDuplicadaError):
        gerenciador.cadastrar_peca("P1", peso=100, cor="azul", comprimento=15)


def test_caixa_fecha_automaticamente_ao_atingir_dez_pecas(gerenciador):
    for indice in range(10):
        gerenciador.cadastrar_peca(f"P{indice}", peso=100, cor="azul", comprimento=15)

    caixas_fechadas = gerenciador.listar_caixas_fechadas()
    assert len(caixas_fechadas) == 1
    assert caixas_fechadas[0].ocupacao == 10
    assert gerenciador.listar_caixas_abertas() == []


def test_decima_primeira_peca_aprovada_abre_nova_caixa(gerenciador):
    for indice in range(10):
        gerenciador.cadastrar_peca(f"P{indice}", peso=100, cor="azul", comprimento=15)

    peca_extra = gerenciador.cadastrar_peca("P10", peso=100, cor="azul", comprimento=15)
    assert peca_extra.caixa_id == 2
    assert len(gerenciador.listar_caixas_fechadas()) == 1
    assert len(gerenciador.listar_caixas_abertas()) == 1


def test_remover_peca_reprovada(gerenciador):
    gerenciador.cadastrar_peca("P1", peso=1, cor="preta", comprimento=1)
    gerenciador.remover_peca("P1")
    with pytest.raises(PecaNaoEncontradaError):
        gerenciador.buscar_peca("P1")


def test_remover_peca_aprovada_em_caixa_aberta(gerenciador):
    gerenciador.cadastrar_peca("P1", peso=100, cor="azul", comprimento=15)
    gerenciador.remover_peca("P1")
    assert gerenciador.caixas[0].ocupacao == 0


def test_remover_peca_em_caixa_fechada_e_bloqueado(gerenciador):
    for indice in range(10):
        gerenciador.cadastrar_peca(f"P{indice}", peso=100, cor="azul", comprimento=15)

    with pytest.raises(RemocaoBloqueadaError):
        gerenciador.remover_peca("P0")


def test_remover_peca_inexistente_levanta_erro(gerenciador):
    with pytest.raises(PecaNaoEncontradaError):
        gerenciador.remover_peca("NAO_EXISTE")


def test_relatorio_final_totais_corretos(gerenciador):
    gerenciador.cadastrar_peca("P1", peso=100, cor="azul", comprimento=15)  # aprovada
    gerenciador.cadastrar_peca("P2", peso=50, cor="preta", comprimento=5)   # reprovada (3 motivos)
    gerenciador.cadastrar_peca("P3", peso=100, cor="vermelha", comprimento=15)  # reprovada (1 motivo)

    relatorio = gerenciador.gerar_relatorio_final()
    assert relatorio.total_cadastradas == 3
    assert relatorio.total_aprovadas == 1
    assert relatorio.total_reprovadas == 2
    assert relatorio.quantidade_caixas_utilizadas == 1
    assert relatorio.quantidade_caixas_abertas == 1
    assert relatorio.taxa_aprovacao_pct == pytest.approx(33.333, rel=1e-3)


def test_persistencia_recupera_estado(tmp_path):
    caminho = tmp_path / "estado.json"
    g1 = GerenciadorProducao(persistir=True, arquivo_estado=caminho)
    g1.cadastrar_peca("P1", peso=100, cor="azul", comprimento=15)

    g2 = GerenciadorProducao(persistir=True, arquivo_estado=caminho)
    assert "P1" in g2.pecas
    assert g2.pecas["P1"].aprovada is True
    assert g2.caixas[0].ocupacao == 1
