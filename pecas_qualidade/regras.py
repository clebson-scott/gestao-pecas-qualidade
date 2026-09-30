"""
regras.py
=========
Regras de negócio de avaliação de qualidade das peças.

Manter as regras em um módulo isolado (em vez de espalhadas pelo menu ou
pela classe de estoque) é uma boa prática de "separação de
responsabilidades" (Single Responsibility Principle): se a fábrica um dia
mudar os critérios de aprovação (ex.: nova faixa de peso), só este arquivo
precisa ser alterado — nada no menu, na persistência ou nos relatórios
muda.

Critérios de aprovação (conforme o desafio):
    - Peso:         95g  <= peso         <= 105g
    - Cor:          azul ou verde
    - Comprimento:  10cm <= comprimento  <= 20cm

Decisão de projeto (documentada por transparência): os limites das faixas
são tratados como **inclusivos** (ex.: uma peça de exatamente 95g é
aprovada). O desafio não especifica se os limites são inclusivos ou
exclusivos; adotamos a interpretação inclusiva por ser a leitura mais
comum de "entre X e Y" em contextos de controle de qualidade industrial
(ISO 2859 e especificações de tolerância costumam tratar os limites de
especificação como parte do intervalo aceito).
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import CorPeca

PESO_MINIMO_G = 95.0
PESO_MAXIMO_G = 105.0
COMPRIMENTO_MINIMO_CM = 10.0
COMPRIMENTO_MAXIMO_CM = 20.0
CORES_APROVADAS = frozenset({CorPeca.AZUL, CorPeca.VERDE})


@dataclass(frozen=True)
class ResultadoAvaliacao:
    """Resultado imutável da avaliação de qualidade de uma peça.

    Attributes:
        aprovada: ``True`` se a peça atendeu a TODOS os critérios.
        motivos: lista de descrições de cada critério não atendido.
            Vazia quando ``aprovada`` é ``True``.
    """

    aprovada: bool
    motivos: tuple[str, ...]


def avaliar_peso(peso: float) -> str | None:
    """Verifica se o peso está dentro da faixa aceita.

    Returns:
        ``None`` se aprovado, ou uma descrição do motivo de reprovação.
    """
    if peso < PESO_MINIMO_G or peso > PESO_MAXIMO_G:
        return (
            f"peso {peso:.1f}g fora da faixa aceita "
            f"[{PESO_MINIMO_G:.0f}g – {PESO_MAXIMO_G:.0f}g]"
        )
    return None


def avaliar_cor(cor: CorPeca) -> str | None:
    """Verifica se a cor está entre as cores aceitas (azul ou verde).

    Returns:
        ``None`` se aprovado, ou uma descrição do motivo de reprovação.
    """
    if cor not in CORES_APROVADAS:
        cores_validas = " ou ".join(c.value for c in CORES_APROVADAS)
        return f"cor '{cor.value}' não aceita (exigido: {cores_validas})"
    return None


def avaliar_comprimento(comprimento: float) -> str | None:
    """Verifica se o comprimento está dentro da faixa aceita.

    Returns:
        ``None`` se aprovado, ou uma descrição do motivo de reprovação.
    """
    if comprimento < COMPRIMENTO_MINIMO_CM or comprimento > COMPRIMENTO_MAXIMO_CM:
        return (
            f"comprimento {comprimento:.1f}cm fora da faixa aceita "
            f"[{COMPRIMENTO_MINIMO_CM:.0f}cm – {COMPRIMENTO_MAXIMO_CM:.0f}cm]"
        )
    return None


def avaliar_peca(peso: float, cor: CorPeca, comprimento: float) -> ResultadoAvaliacao:
    """Avalia uma peça contra todos os critérios de qualidade.

    Roda TODAS as verificações (não interrompe na primeira falha) para que
    o relatório final possa mostrar, por exemplo, "peso E comprimento fora
    da faixa" em vez de só o primeiro problema encontrado — informação
    mais útil para o time de produção diagnosticar a causa raiz.

    Args:
        peso: peso da peça em gramas.
        cor: cor da peça (já normalizada).
        comprimento: comprimento da peça em centímetros.

    Returns:
        Um :class:`ResultadoAvaliacao` com o veredito e os motivos.
    """
    verificacoes = (
        avaliar_peso(peso),
        avaliar_cor(cor),
        avaliar_comprimento(comprimento),
    )
    motivos = tuple(motivo for motivo in verificacoes if motivo is not None)
    return ResultadoAvaliacao(aprovada=(len(motivos) == 0), motivos=motivos)
