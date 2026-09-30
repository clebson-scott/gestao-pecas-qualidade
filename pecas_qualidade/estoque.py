"""
estoque.py
==========
Núcleo lógico do sistema: a classe :class:`GerenciadorProducao`.

Esta classe orquestra tudo o que o desafio pede:
    1. Cadastro de peças (com avaliação automática de qualidade).
    2. Armazenamento das peças aprovadas em caixas de capacidade limitada,
       com fechamento automático e abertura de uma nova caixa.
    3. Consulta de peças por status (aprovada/reprovada).
    4. Remoção de peças cadastradas (respeitando a imutabilidade de caixas
       fechadas).
    5. Geração de relatórios consolidados.

Ela não sabe nada sobre menus, terminal ou entrada de usuário — isso é
responsabilidade do módulo ``main.py`` (interface). Essa separação entre
"lógica" e "interface" é o que permite, por exemplo, reaproveitar esta
mesma classe numa futura API REST ou numa interface gráfica, sem reescrever
uma linha da regra de negócio (ver seção "Como isso evoluiria" no
README/relatório teórico).
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .excecoes import PecaDuplicadaError, PecaNaoEncontradaError, RemocaoBloqueadaError
from .models import Caixa, CorPeca, Peca, StatusPeca
from .persistencia import ARQUIVO_ESTADO_PADRAO, carregar_estado, salvar_estado
from .regras import avaliar_peca

logger = logging.getLogger(__name__)


@dataclass
class RelatorioFinal:
    """Estrutura de dados do relatório consolidado (item 5 do desafio).

    Ter uma dataclass própria para o relatório (em vez de retornar um
    dicionário genérico) permite formatar a saída de formas diferentes
    (texto no terminal, arquivo .txt, futuramente PDF/dashboard) a partir
    da MESMA fonte de dados, sem duplicar a lógica de cálculo.
    """

    total_cadastradas: int
    total_aprovadas: int
    total_reprovadas: int
    motivos_reprovacao: dict[str, int]
    quantidade_caixas_utilizadas: int
    quantidade_caixas_fechadas: int
    quantidade_caixas_abertas: int
    taxa_aprovacao_pct: float

    def __str__(self) -> str:
        linhas = [
            "=" * 56,
            " RELATÓRIO CONSOLIDADO DE PRODUÇÃO E QUALIDADE".center(56),
            "=" * 56,
            f"Total de peças cadastradas ..................... {self.total_cadastradas}",
            f"Total de peças APROVADAS ....................... {self.total_aprovadas}",
            f"Total de peças REPROVADAS ...................... {self.total_reprovadas}",
            f"Taxa de aprovação ............................... {self.taxa_aprovacao_pct:.1f}%",
            "-" * 56,
            "Motivos de reprovação (peças podem ter mais de um):",
        ]
        if self.motivos_reprovacao:
            for motivo, quantidade in sorted(
                self.motivos_reprovacao.items(), key=lambda item: -item[1]
            ):
                linhas.append(f"  - {motivo}: {quantidade} ocorrência(s)")
        else:
            linhas.append("  - nenhuma reprovação registrada")
        linhas += [
            "-" * 56,
            f"Caixas utilizadas (abertas + fechadas) ......... {self.quantidade_caixas_utilizadas}",
            f"  - fechadas (capacidade máxima atingida) ...... {self.quantidade_caixas_fechadas}",
            f"  - em aberto (aguardando novas peças) ......... {self.quantidade_caixas_abertas}",
            "=" * 56,
        ]
        return "\n".join(linhas)


class GerenciadorProducao:
    """Gerencia o ciclo de vida das peças e das caixas de armazenamento.

    Attributes:
        pecas: dicionário ``{id_peca: Peca}`` com todas as peças cadastradas
            (aprovadas e reprovadas).
        caixas: lista de todas as :class:`Caixa` já criadas, na ordem de
            criação. A última posição é sempre a caixa "corrente"
            (aberta) até ela fechar e uma nova ser criada.
        persistir: quando ``True`` (padrão), toda alteração é
            automaticamente salva em disco via ``persistencia.py``.
    """

    def __init__(
        self, persistir: bool = True, arquivo_estado: Path = ARQUIVO_ESTADO_PADRAO
    ) -> None:
        self.pecas: dict[str, Peca] = {}
        self.caixas: list[Caixa] = []
        self._proximo_id_caixa: int = 1
        self.persistir = persistir
        self._arquivo_estado = arquivo_estado

        if persistir:
            self.pecas, self.caixas, self._proximo_id_caixa = carregar_estado(arquivo_estado)

    # ------------------------------------------------------------------ #
    # 1. Cadastro
    # ------------------------------------------------------------------ #
    def cadastrar_peca(
        self, id_peca: str, peso: float, cor: str | CorPeca, comprimento: float
    ) -> Peca:
        """Cadastra uma nova peça, avalia sua qualidade e a armazena.

        Args:
            id_peca: identificador único da peça (definido pelo operador).
            peso: peso em gramas.
            cor: cor da peça (string livre ou já normalizada).
            comprimento: comprimento em centímetros.

        Returns:
            A :class:`Peca` criada, já com ``status`` e ``caixa_id`` definidos.

        Raises:
            PecaDuplicadaError: se já existir uma peça cadastrada com este id.
            ValueError: se a cor informada não for reconhecida.
        """
        if id_peca in self.pecas:
            raise PecaDuplicadaError(f"Já existe uma peça cadastrada com o id '{id_peca}'.")

        cor_normalizada = cor if isinstance(cor, CorPeca) else CorPeca.normalizar(cor)
        resultado = avaliar_peca(peso=peso, cor=cor_normalizada, comprimento=comprimento)

        peca = Peca(
            id=id_peca,
            peso=peso,
            cor=cor_normalizada,
            comprimento=comprimento,
            status=StatusPeca.APROVADA if resultado.aprovada else StatusPeca.REPROVADA,
            motivos_reprovacao=list(resultado.motivos),
        )

        if resultado.aprovada:
            caixa = self._caixa_corrente()
            caixa.adicionar(peca.id)
            peca.caixa_id = caixa.id
            logger.info("Peça %s APROVADA e armazenada na caixa #%s.", peca.id, caixa.id)
        else:
            logger.info("Peça %s REPROVADA: %s.", peca.id, "; ".join(resultado.motivos))

        self.pecas[peca.id] = peca
        self._salvar()
        return peca

    def _caixa_corrente(self) -> Caixa:
        """Retorna a caixa aberta atual, criando uma nova se necessário.

        Esta é a implementação da regra "fechar a caixa quando atingir a
        capacidade máxima e iniciar uma nova": nunca reabrimos uma caixa
        fechada; sempre que não há caixa aberta disponível, uma nova é
        criada com o próximo id sequencial.
        """
        if self.caixas and not self.caixas[-1].fechada:
            return self.caixas[-1]

        nova_caixa = Caixa(id=self._proximo_id_caixa)
        self.caixas.append(nova_caixa)
        self._proximo_id_caixa += 1
        logger.info("Nova caixa #%s aberta.", nova_caixa.id)
        return nova_caixa

    # ------------------------------------------------------------------ #
    # 2. Consultas
    # ------------------------------------------------------------------ #
    def listar_por_status(self, status: StatusPeca) -> list[Peca]:
        """Retorna todas as peças com o status informado, na ordem de cadastro."""
        return [peca for peca in self.pecas.values() if peca.status == status]

    def listar_caixas_fechadas(self) -> list[Caixa]:
        """Retorna todas as caixas já fechadas (capacidade máxima atingida)."""
        return [caixa for caixa in self.caixas if caixa.fechada]

    def listar_caixas_abertas(self) -> list[Caixa]:
        """Retorna todas as caixas ainda abertas (deveria ser 0 ou 1, nunca mais)."""
        return [caixa for caixa in self.caixas if not caixa.fechada]

    def buscar_peca(self, id_peca: str) -> Peca:
        """Busca uma peça pelo id.

        Raises:
            PecaNaoEncontradaError: se não houver peça com esse id.
        """
        try:
            return self.pecas[id_peca]
        except KeyError as erro:
            raise PecaNaoEncontradaError(f"Nenhuma peça encontrada com o id '{id_peca}'.") from erro

    # ------------------------------------------------------------------ #
    # 3. Remoção
    # ------------------------------------------------------------------ #
    def remover_peca(self, id_peca: str) -> Peca:
        """Remove uma peça cadastrada do sistema.

        Regra de negócio: peças aprovadas que já estão dentro de uma caixa
        **fechada** não podem ser removidas (a caixa fechada é imutável —
        ver docstring de :class:`models.Caixa`). Peças reprovadas, ou
        aprovadas numa caixa ainda aberta, podem ser removidas livremente.

        Args:
            id_peca: id da peça a remover.

        Returns:
            A :class:`Peca` removida.

        Raises:
            PecaNaoEncontradaError: se o id não existir.
            RemocaoBloqueadaError: se a peça estiver numa caixa já fechada.
        """
        peca = self.buscar_peca(id_peca)

        if peca.caixa_id is not None:
            caixa = self._buscar_caixa(peca.caixa_id)
            if caixa.fechada:
                raise RemocaoBloqueadaError(
                    f"A peça '{id_peca}' está na caixa #{caixa.id}, que já está fechada "
                    "e é imutável. Remoção não permitida."
                )
            caixa.remover(id_peca)

        del self.pecas[id_peca]
        logger.info("Peça %s removida do sistema.", id_peca)
        self._salvar()
        return peca

    def _buscar_caixa(self, id_caixa: int) -> Caixa:
        for caixa in self.caixas:
            if caixa.id == id_caixa:
                return caixa
        raise PecaNaoEncontradaError(f"Caixa #{id_caixa} não encontrada (estado inconsistente).")

    # ------------------------------------------------------------------ #
    # 4. Relatório consolidado
    # ------------------------------------------------------------------ #
    def gerar_relatorio_final(self) -> RelatorioFinal:
        """Consolida as métricas exigidas pelo desafio num objeto único.

        Returns:
            Um :class:`RelatorioFinal` com todos os totais e motivos.
        """
        aprovadas = self.listar_por_status(StatusPeca.APROVADA)
        reprovadas = self.listar_por_status(StatusPeca.REPROVADA)

        contador_motivos: Counter[str] = Counter()
        for peca in reprovadas:
            contador_motivos.update(peca.motivos_reprovacao)

        total = len(self.pecas)
        taxa_aprovacao = (len(aprovadas) / total * 100.0) if total else 0.0

        return RelatorioFinal(
            total_cadastradas=total,
            total_aprovadas=len(aprovadas),
            total_reprovadas=len(reprovadas),
            motivos_reprovacao=dict(contador_motivos),
            quantidade_caixas_utilizadas=len(self.caixas),
            quantidade_caixas_fechadas=len(self.listar_caixas_fechadas()),
            quantidade_caixas_abertas=len(self.listar_caixas_abertas()),
            taxa_aprovacao_pct=taxa_aprovacao,
        )

    # ------------------------------------------------------------------ #
    # Persistência
    # ------------------------------------------------------------------ #
    def _salvar(self) -> None:
        if self.persistir:
            salvar_estado(self.pecas, self.caixas, self._proximo_id_caixa, self._arquivo_estado)
