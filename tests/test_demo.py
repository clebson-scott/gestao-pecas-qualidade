"""Smoke tests da demonstração automática (demo.py).

A demo é executável de apresentação — se ela roda até o fim sem exceção e
imprime o essencial, o fluxo principal do sistema está funcionando de
ponta a ponta. Esses testes travam exatamente isso.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pecas_qualidade import demo
from pecas_qualidade.excecoes import RemocaoBloqueadaError


def test_demo_rodar_completa_sem_excecao(tmp_path, capsys):
    demo.rodar_demo(tmp_path / "estado_demo.json")
    saida = capsys.readouterr().out

    # O cenário completo executa: 15 peças, 12 aprovadas, 3 reprovadas.
    assert "DEMONSTRAÇÃO AUTOMÁTICA" in saida
    assert "[1/4] Cadastrando 15 peças" in saida
    assert "R01: Reprovada" in saida
    assert "Caixa #1 [FECHADA] — 10/10 peças" in saida
    assert "Caixa #2 [aberta] — 2/10 peças" in saida
    assert "RELATÓRIO CONSOLIDADO" in saida
    assert "Taxa de aprovação" in saida
    assert "Demonstração concluída com sucesso." in saida


def test_demo_bloqueia_remocao_em_caixa_fechada(tmp_path, capsys):
    demo.rodar_demo(tmp_path / "estado_demo.json")
    saida = capsys.readouterr().out
    # A seção [3/4] demonstra a regra de imutabilidade ao vivo.
    assert "[3/4] Regra de imutabilidade" in saida
    assert "Bloqueado como esperado" in saida
    assert RemocaoBloqueadaError.__name__ in saida


def test_demo_com_estado_temporario_nao_suja_disco(tmp_path, capsys, monkeypatch):
    # Por padrão (arquivo None) a demo cria estado temporário e o deixa
    # fora do diretório corrente: nada é gravado no projeto.
    arquivos_antes = set(Path.cwd().iterdir())
    demo.rodar_demo(None)
    capsys.readouterr()
    arquivos_depois = set(Path.cwd().iterdir())
    assert arquivos_antes == arquivos_depois
