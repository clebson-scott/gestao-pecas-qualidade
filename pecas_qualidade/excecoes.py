"""
excecoes.py
===========
Exceções customizadas do domínio.

Usar exceções específicas (em vez de ``Exception`` genérica ou ``ValueError``
solto) deixa o código autoexplicativo: quem lê ``except PecaDuplicadaError``
entende imediatamente qual regra de negócio foi violada, sem precisar ler a
mensagem de erro inteira.
"""


class ErroDominioPecas(Exception):
    """Classe base para todas as exceções de domínio deste sistema."""


class PecaDuplicadaError(ErroDominioPecas):
    """Levantada ao tentar cadastrar uma peça com um id já existente."""


class PecaNaoEncontradaError(ErroDominioPecas):
    """Levantada ao referenciar um id de peça que não está cadastrado."""


class RemocaoBloqueadaError(ErroDominioPecas):
    """Levantada ao tentar remover uma peça que está numa caixa já fechada.

    Caixas fechadas são imutáveis por design (ver docstring de
    ``models.Caixa``) — essa regra existe para preservar a rastreabilidade
    de lotes já lacrados, tal como num processo real de controle de
    qualidade industrial.
    """
