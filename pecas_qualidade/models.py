"""
models.py
=========
Modelos de domínio do sistema de Gestão de Peças, Qualidade e Armazenamento.

Este módulo define as estruturas de dados centrais do sistema:

- :class:`Peca`: representa uma peça produzida na linha de montagem, com seus
  atributos físicos (peso, cor, comprimento) e o resultado da inspeção de
  qualidade (aprovada/reprovada + motivo).
- :class:`Caixa`: representa uma caixa de armazenamento de peças aprovadas,
  com capacidade fixa e regra de fechamento automático.

Optamos por ``dataclasses`` (PEP 557) em vez de dicionários soltos porque:
1. Dão tipagem estática clara (facilita manutenção e leitura).
2. Geram automaticamente ``__repr__``, ``__eq__`` e permitem serialização
   simples via ``dataclasses.asdict``.
3. Deixam explícito, no próprio construtor, quais campos são obrigatórios.

Autor: Clebson Scott
Disciplina: Algoritmos e Lógica de Programação — UniFECAF
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional


class StatusPeca(str, Enum):
    """Enumeração dos possíveis estados de uma peça após a inspeção.

    Usar um Enum (em vez de strings soltas como "aprovada"/"reprovada")
    evita erros de digitação espalhados pelo código e deixa o fluxo de
    decisão auto-documentado.
    """

    APROVADA = "Aprovada"
    REPROVADA = "Reprovada"


class CorPeca(str, Enum):
    """Cores de peça aceitas como entrada válida pelo sistema.

    O critério de qualidade exige azul ou verde para aprovação, mas o
    sistema aceita cadastrar peças de qualquer cor conhecida — a decisão
    de aprovar/reprovar é feita pelas regras de negócio (ver ``regras.py``),
    não pela validação de entrada. Isso separa "dado válido" de
    "peça aprovada", que são conceitos diferentes.
    """

    AZUL = "Azul"
    VERDE = "Verde"
    VERMELHA = "Vermelha"
    AMARELA = "Amarela"
    PRETA = "Preta"
    BRANCA = "Branca"
    CINZA = "Cinza"
    LARANJA = "Laranja"

    @classmethod
    def normalizar(cls, valor: str) -> "CorPeca":
        """Converte uma string livre (com acentos, caixa alta/baixa) na
        cor equivalente do Enum.

        Args:
            valor: texto digitado pelo usuário, ex.: "AZUL", "azul ", "Verde".

        Raises:
            ValueError: se a cor não for reconhecida pelo sistema.
        """
        mapa_acentos = str.maketrans("áàâãéèêíìîóòôõúùûç", "aaaaeeeiiiooooouuc")
        chave = valor.strip().lower().translate(mapa_acentos)
        equivalencias = {
            "azul": cls.AZUL,
            "verde": cls.VERDE,
            "vermelha": cls.VERMELHA,
            "vermelho": cls.VERMELHA,
            "amarela": cls.AMARELA,
            "amarelo": cls.AMARELA,
            "preta": cls.PRETA,
            "preto": cls.PRETA,
            "branca": cls.BRANCA,
            "branco": cls.BRANCA,
            "cinza": cls.CINZA,
            "laranja": cls.LARANJA,
        }
        if chave not in equivalencias:
            aceitas = ", ".join(sorted({e.value for e in equivalencias.values()}))
            raise ValueError(
                f"Cor '{valor}' não reconhecida. Cores aceitas: {aceitas}."
            )
        return equivalencias[chave]


@dataclass
class Peca:
    """Representa uma peça produzida na linha de montagem.

    Attributes:
        id: identificador único da peça (definido pelo operador/sistema).
        peso: peso da peça em gramas (g).
        cor: cor da peça, já normalizada em :class:`CorPeca`.
        comprimento: comprimento da peça em centímetros (cm).
        status: resultado da inspeção — preenchido por ``regras.avaliar_peca``.
        motivos_reprovacao: lista de critérios que a peça não atendeu.
            Fica vazia quando a peça é aprovada.
        caixa_id: identificador da caixa onde a peça foi armazenada
            (``None`` se a peça foi reprovada, pois reprovadas não são
            armazenadas em caixas).
        criada_em: timestamp de cadastro, útil para auditoria/rastreio.
    """

    id: str
    peso: float
    cor: CorPeca
    comprimento: float
    status: StatusPeca = StatusPeca.REPROVADA
    motivos_reprovacao: list[str] = field(default_factory=list)
    caixa_id: Optional[int] = None
    criada_em: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @property
    def aprovada(self) -> bool:
        """Atalho booleano equivalente a ``status == StatusPeca.APROVADA``."""
        return self.status == StatusPeca.APROVADA

    def to_dict(self) -> dict:
        """Serializa a peça para um dicionário simples (JSON-friendly)."""
        dados = asdict(self)
        dados["cor"] = self.cor.value
        dados["status"] = self.status.value
        return dados

    @classmethod
    def from_dict(cls, dados: dict) -> "Peca":
        """Reconstrói uma :class:`Peca` a partir de um dicionário (ex.: JSON)."""
        return cls(
            id=dados["id"],
            peso=dados["peso"],
            cor=CorPeca(dados["cor"]),
            comprimento=dados["comprimento"],
            status=StatusPeca(dados["status"]),
            motivos_reprovacao=list(dados.get("motivos_reprovacao", [])),
            caixa_id=dados.get("caixa_id"),
            criada_em=dados.get("criada_em", datetime.now().isoformat(timespec="seconds")),
        )

    def __str__(self) -> str:
        base = (
            f"Peça #{self.id} | {self.peso:.1f}g | {self.cor.value} | "
            f"{self.comprimento:.1f}cm | {self.status.value}"
        )
        if self.motivos_reprovacao:
            base += f" (motivo: {', '.join(self.motivos_reprovacao)})"
        if self.caixa_id is not None:
            base += f" [Caixa #{self.caixa_id}]"
        return base


@dataclass
class Caixa:
    """Representa uma caixa de armazenamento de peças aprovadas.

    Regra de negócio central: uma caixa tem capacidade fixa
    (``CAPACIDADE_MAXIMA``) e é fechada automaticamente ao atingir esse
    limite — nunca recebe uma 11ª peça. Uma vez fechada, a caixa é
    **imutável**: nenhuma peça pode ser adicionada ou removida dela. Essa
    imutabilidade espelha uma prática real de controle de qualidade
    industrial (lote fechado = lote rastreável e auditável).

    Attributes:
        id: identificador sequencial da caixa (1, 2, 3, ...).
        capacidade_maxima: número máximo de peças por caixa (10, fixo pelo
            desafio, mas mantido configurável para reuso/teste).
        pecas_ids: lista dos ids das peças aprovadas armazenadas nesta caixa.
        fechada: ``True`` quando a caixa atingiu a capacidade máxima.
        fechada_em: timestamp de fechamento (``None`` enquanto aberta).
    """

    id: int
    capacidade_maxima: int = 10
    pecas_ids: list[str] = field(default_factory=list)
    fechada: bool = False
    fechada_em: Optional[str] = None

    @property
    def ocupacao(self) -> int:
        """Quantidade de peças atualmente armazenadas na caixa."""
        return len(self.pecas_ids)

    @property
    def vagas_disponiveis(self) -> int:
        """Quantas peças ainda cabem nesta caixa."""
        return self.capacidade_maxima - self.ocupacao

    def adicionar(self, peca_id: str) -> None:
        """Adiciona o id de uma peça à caixa e a fecha se atingir a capacidade.

        Raises:
            RuntimeError: se a caixa já estiver fechada ou já estiver cheia
                (defesa extra — o chamador deve verificar antes, mas o
                método nunca deixa o invariante de capacidade ser violado).
        """
        if self.fechada:
            raise RuntimeError(f"Caixa #{self.id} já está fechada; não é possível adicionar peças.")
        if self.ocupacao >= self.capacidade_maxima:
            raise RuntimeError(f"Caixa #{self.id} já atingiu a capacidade máxima.")

        self.pecas_ids.append(peca_id)
        if self.ocupacao >= self.capacidade_maxima:
            self.fechada = True
            self.fechada_em = datetime.now().isoformat(timespec="seconds")

    def remover(self, peca_id: str) -> None:
        """Remove uma peça da caixa (somente permitido em caixas abertas).

        Raises:
            RuntimeError: se a caixa estiver fechada.
            ValueError: se a peça não estiver nesta caixa.
        """
        if self.fechada:
            raise RuntimeError(
                f"Caixa #{self.id} está fechada e é imutável; a peça não pode ser removida."
            )
        if peca_id not in self.pecas_ids:
            raise ValueError(f"Peça #{peca_id} não está na caixa #{self.id}.")
        self.pecas_ids.remove(peca_id)

    def to_dict(self) -> dict:
        """Serializa a caixa para um dicionário simples (JSON-friendly)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, dados: dict) -> "Caixa":
        """Reconstrói uma :class:`Caixa` a partir de um dicionário (ex.: JSON)."""
        return cls(
            id=dados["id"],
            capacidade_maxima=dados.get("capacidade_maxima", 10),
            pecas_ids=list(dados.get("pecas_ids", [])),
            fechada=dados.get("fechada", False),
            fechada_em=dados.get("fechada_em"),
        )

    def __str__(self) -> str:
        estado = "FECHADA" if self.fechada else "aberta"
        return f"Caixa #{self.id} [{estado}] — {self.ocupacao}/{self.capacidade_maxima} peças"
