"""Testes unitários para as regras de qualidade (regras.py)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pecas_qualidade.models import CorPeca
from pecas_qualidade.regras import avaliar_peca


def test_peca_perfeita_e_aprovada():
    resultado = avaliar_peca(peso=100, cor=CorPeca.AZUL, comprimento=15)
    assert resultado.aprovada is True
    assert resultado.motivos == ()


def test_limites_inferiores_inclusivos():
    resultado = avaliar_peca(peso=95, cor=CorPeca.VERDE, comprimento=10)
    assert resultado.aprovada is True


def test_limites_superiores_inclusivos():
    resultado = avaliar_peca(peso=105, cor=CorPeca.AZUL, comprimento=20)
    assert resultado.aprovada is True


def test_peso_abaixo_do_minimo_reprova():
    resultado = avaliar_peca(peso=94.9, cor=CorPeca.AZUL, comprimento=15)
    assert resultado.aprovada is False
    assert any("peso" in motivo for motivo in resultado.motivos)


def test_peso_acima_do_maximo_reprova():
    resultado = avaliar_peca(peso=105.1, cor=CorPeca.AZUL, comprimento=15)
    assert resultado.aprovada is False
    assert any("peso" in motivo for motivo in resultado.motivos)


def test_cor_invalida_reprova():
    resultado = avaliar_peca(peso=100, cor=CorPeca.VERMELHA, comprimento=15)
    assert resultado.aprovada is False
    assert any("cor" in motivo for motivo in resultado.motivos)


def test_comprimento_fora_da_faixa_reprova():
    resultado = avaliar_peca(peso=100, cor=CorPeca.VERDE, comprimento=25)
    assert resultado.aprovada is False
    assert any("comprimento" in motivo for motivo in resultado.motivos)


def test_multiplos_motivos_sao_todos_reportados():
    resultado = avaliar_peca(peso=50, cor=CorPeca.PRETA, comprimento=5)
    assert resultado.aprovada is False
    assert len(resultado.motivos) == 3


def test_normalizacao_de_cor_aceita_variacoes():
    assert CorPeca.normalizar("AZUL") == CorPeca.AZUL
    assert CorPeca.normalizar(" verde ") == CorPeca.VERDE
    assert CorPeca.normalizar("Vermelho") == CorPeca.VERMELHA


def test_normalizacao_de_cor_invalida_levanta_erro():
    import pytest

    with pytest.raises(ValueError):
        CorPeca.normalizar("roxo")
