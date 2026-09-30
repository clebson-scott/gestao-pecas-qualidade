"""Testes dos caminhos de erro e casos de borda (models, persistencia, main)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pecas_qualidade.excecoes import PecaNaoEncontradaError
from pecas_qualidade.models import Caixa, CorPeca, Peca, StatusPeca
from pecas_qualidade.persistencia import carregar_estado, salvar_estado


# --------------------------------------------------------------------- #
# models.Caixa — invariantes guardados por exceção
# --------------------------------------------------------------------- #
def test_caixa_fechada_recusa_adicionar():
    caixa = Caixa(id=1, capacidade_maxima=2, pecas_ids=["A", "B"], fechada=True)
    with pytest.raises(RuntimeError, match="já está fechada"):
        caixa.adicionar("C")


def test_caixa_cheia_recusa_adicionar_mesmo_aberta():
    # Capacidade 2 com 2 peças mas sem flag fechada: estado inconsistente
    # defendido pela guarda do método.
    caixa = Caixa(id=1, capacidade_maxima=2, pecas_ids=["A", "B"])
    with pytest.raises(RuntimeError, match="capacidade máxima"):
        caixa.adicionar("C")


def test_caixa_aberta_remove_peca():
    caixa = Caixa(id=1, pecas_ids=["A", "B"])
    caixa.remover("A")
    assert caixa.pecas_ids == ["B"]
    assert caixa.vagas_disponiveis == 9


def test_caixa_fechada_recusa_remover():
    caixa = Caixa(id=1, pecas_ids=["A"], fechada=True)
    with pytest.raises(RuntimeError, match="imutável"):
        caixa.remover("A")


def test_caixa_recusa_remover_peca_ausente():
    caixa = Caixa(id=1)
    with pytest.raises(ValueError, match="não está na caixa"):
        caixa.remover("X")


def test_peca_from_dict_roundtrip():
    dados = {
        "id": "P1",
        "peso": 100.0,
        "cor": "Azul",
        "comprimento": 15.0,
        "status": "Aprovada",
        "motivos_reprovacao": [],
        "caixa_id": 1,
        "criada_em": "2026-09-30T10:00:00",
    }
    peca = Peca.from_dict(dados)
    assert peca.to_dict() == dados
    assert peca.aprovada is True


def test_peca_str_inclui_motivos_e_caixa():
    reprovada = Peca(
        id="R",
        peso=50,
        cor=CorPeca.PRETA,
        comprimento=5,
        status=StatusPeca.REPROVADA,
        motivos_reprovacao=["peso"],
    )
    aprovada = Peca(
        id="A",
        peso=100,
        cor=CorPeca.AZUL,
        comprimento=15,
        status=StatusPeca.APROVADA,
        caixa_id=3,
    )
    assert "motivo: peso" in str(reprovada)
    assert "Caixa #3" in str(aprovada)


def test_relatorio_final_str_sem_reprovacoes():
    from pecas_qualidade.estoque import RelatorioFinal

    rel = RelatorioFinal(
        total_cadastradas=1,
        total_aprovadas=1,
        total_reprovadas=0,
        motivos_reprovacao={},
        quantidade_caixas_utilizadas=1,
        quantidade_caixas_fechadas=0,
        quantidade_caixas_abertas=1,
        taxa_aprovacao_pct=100.0,
    )
    texto = str(rel)
    assert "nenhuma reprovação registrada" in texto
    assert "100.0%" in texto


# --------------------------------------------------------------------- #
# persistencia — robustez contra arquivos corrompidos/inacessíveis
# --------------------------------------------------------------------- #
def test_carregar_estado_arquivo_inexistente_retorna_vazio(tmp_path):
    pecas, caixas, proximo = carregar_estado(tmp_path / "nao_existe.json")
    assert pecas == {}
    assert caixas == []
    assert proximo == 1


def test_carregar_estado_arquivo_corrompido_retorna_vazio(tmp_path):
    caminho = tmp_path / "corrompido.json"
    caminho.write_text("{isso não é json válido", encoding="utf-8")
    pecas, caixas, proximo = carregar_estado(caminho)
    assert pecas == {}
    assert caixas == []
    assert proximo == 1


def test_carregar_estado_estrutura_incompleta_nao_quebra(tmp_path):
    caminho = tmp_path / "incompleto.json"
    caminho.write_text('{"versao": 1}', encoding="utf-8")
    pecas, caixas, _ = carregar_estado(caminho)
    assert pecas == {}
    assert caixas == []


def test_salvar_estado_em_caminho_invalido_nao_quebra(tmp_path):
    # Caminho dentro de um "arquivo tratado como diretório": impossível de
    # gravar — o sistema deve logar o erro e continuar operando.
    alvo = tmp_path / "arquivo.txt"
    alvo.write_text("sou um arquivo", encoding="utf-8")
    salvar_estado({}, [], 1, alvo / "subdir" / "estado.json")  # não deve lançar


def test_gerenciador_buscar_caixa_inexistente_avisa(tmp_path):
    from pecas_qualidade.estoque import GerenciadorProducao

    g = GerenciadorProducao(persistir=False, arquivo_estado=tmp_path / "e.json")
    with pytest.raises(PecaNaoEncontradaError):
        g._buscar_caixa(999)
