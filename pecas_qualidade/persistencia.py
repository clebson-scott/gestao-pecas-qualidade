"""
persistencia.py
================
Camada de persistência do sistema: salva e recupera o estado completo
(peças + caixas + contadores) em um arquivo JSON local.

Por quê persistência?
O desafio não exige explicitamente que os dados sobrevivam entre execuções,
mas um sistema de controle de produção real jamais poderia "esquecer" tudo
a cada reinício — seria inútil para uma fábrica que roda 24/7. Adicionamos
essa camada como um "vá além" que também facilita a correção do trabalho
(o professor pode fechar e reabrir o programa sem perder o que foi
cadastrado na demonstração).

O arquivo é gravado em formato JSON human-readable (não um pickle binário)
de propósito: qualquer pessoa pode abrir ``estado_producao.json`` num editor
de texto e auditar exatamente o que o sistema tem armazenado — importante
num contexto de rastreabilidade industrial.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .models import Caixa, Peca

logger = logging.getLogger(__name__)

ARQUIVO_ESTADO_PADRAO = Path(__file__).resolve().parent / "estado_producao.json"


def salvar_estado(
    pecas: dict[str, Peca],
    caixas: list[Caixa],
    proximo_id_caixa: int,
    caminho: Path = ARQUIVO_ESTADO_PADRAO,
) -> None:
    """Grava o estado completo do sistema em disco, em formato JSON.

    Args:
        pecas: dicionário {id_peca: Peca} com todas as peças cadastradas.
        caixas: lista de todas as caixas (abertas e fechadas).
        proximo_id_caixa: contador para o próximo id de caixa a ser criado.
        caminho: arquivo de destino (parametrizável para facilitar testes).
    """
    estado = {
        "versao": 1,
        "pecas": [peca.to_dict() for peca in pecas.values()],
        "caixas": [caixa.to_dict() for caixa in caixas],
        "proximo_id_caixa": proximo_id_caixa,
    }
    try:
        caminho.write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Estado salvo em %s (%d peças, %d caixas).", caminho, len(pecas), len(caixas))
    except OSError as erro:
        # Falha ao salvar não deve derrubar o programa: registramos o erro
        # e deixamos o usuário continuar operando em memória.
        logger.error("Não foi possível salvar o estado em %s: %s", caminho, erro)


def carregar_estado(
    caminho: Path = ARQUIVO_ESTADO_PADRAO,
) -> tuple[dict[str, Peca], list[Caixa], int]:
    """Lê o estado do sistema a partir do disco, se o arquivo existir.

    Args:
        caminho: arquivo de origem (parametrizável para facilitar testes).

    Returns:
        Uma tupla ``(pecas, caixas, proximo_id_caixa)``. Se o arquivo não
        existir ou estiver corrompido, retorna um estado vazio (o sistema
        simplesmente começa do zero, sem quebrar).
    """
    if not caminho.exists():
        logger.info("Nenhum estado anterior encontrado em %s; iniciando vazio.", caminho)
        return {}, [], 1

    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        pecas = {p["id"]: Peca.from_dict(p) for p in dados.get("pecas", [])}
        caixas = [Caixa.from_dict(c) for c in dados.get("caixas", [])]
        proximo_id_caixa = dados.get("proximo_id_caixa", (len(caixas) + 1))
        logger.info("Estado carregado de %s (%d peças, %d caixas).", caminho, len(pecas), len(caixas))
        return pecas, caixas, proximo_id_caixa
    except (json.JSONDecodeError, KeyError, OSError) as erro:
        logger.warning(
            "Estado em %s está corrompido ou ilegível (%s); iniciando vazio.", caminho, erro
        )
        return {}, [], 1
