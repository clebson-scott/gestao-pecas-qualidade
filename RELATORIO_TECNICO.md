---
title: "Desafio de Automação Digital: Gestão de Peças, Qualidade e Armazenamento"
subtitle: "Parte Teórica — Análise e Discussão"
author: "Clebson Scott"
disciplina: "Algoritmos e Lógica de Programação"
instituicao: "UniFECAF"
---

# Desafio de Automação Digital: Gestão de Peças, Qualidade e Armazenamento

**Parte Teórica — Análise e Discussão**

**Autor:** Clebson Scott
**Disciplina:** Algoritmos e Lógica de Programação
**Instituição:** UniFECAF
**Repositório do código-fonte:** https://github.com/clebson-scott/gestao-pecas-qualidade

---

## 1. Contextualização do desafio

### 1.1 Por que a automação é importante na indústria

O desafio proposto retrata uma situação extremamente comum em ambientes
de manufatura de pequeno e médio porte: a inspeção de qualidade ainda
feita manualmente, item a item, por um operador humano com régua, balança
e uma tabela de referência de cores. Esse modelo carrega três fragilidades
estruturais que a automação digital ataca diretamente:

1. **Inconsistência de julgamento.** Um operador humano, ao longo de um
   turno de oito horas, sofre fadiga visual e cognitiva. A régua e a
   balança não erram, mas a leitura e a decisão ("está dentro do
   critério?") sim. Um sistema automatizado aplica exatamente o mesmo
   critério, na milésima peça e na primeira, sem variação.
2. **Custo de atraso.** Cada peça inspecionada manualmente consome tempo
   de um profissional que poderia estar em uma atividade de maior valor
   agregado. Em escala, esse tempo se traduz diretamente em custo de
   operação e em gargalo de produção — a linha de montagem não pode
   andar mais rápido que a inspeção.
3. **Ausência de rastreabilidade em tempo real.** Quando o relatório de
   qualidade só é compilado ao final do turno (ou, pior, ao final da
   semana, numa planilha), qualquer problema sistemático na matéria-prima
   ou na calibração de uma máquina só é percebido depois que centenas de
   peças já foram produzidas fora do padrão.

A automação digital, mesmo em um protótipo simples como o deste desafio,
ataca os três pontos simultaneamente: aplica um critério **determinístico
e auditável** a cada peça, no **instante do cadastro**, e mantém um
relatório **sempre atualizado e disponível sob demanda** — sem esperar o
fim do turno.

### 1.2 O problema em termos de engenharia de software

Reduzido à sua essência lógica, o desafio pede três coisas encadeadas:

1. Uma função de **classificação binária com múltiplos critérios**
   (peso, cor, comprimento) que decide "aprovada" ou "reprovada" e, no
   segundo caso, explica o motivo.
2. Uma estrutura de **agrupamento com capacidade limitada e fechamento
   automático** (as caixas de 10 peças) — um problema clássico de
   "bin packing" simplificado, onde os itens (peças aprovadas) chegam
   em fluxo e precisam ser distribuídos em contêineres de tamanho fixo.
3. Uma camada de **agregação/relatório** sobre os dados acumulados nos
   dois pontos anteriores.

Essa decomposição — avaliação, armazenamento, relatório — é exatamente a
que guiou a arquitetura do código (ver seção 2).

---

## 2. Como o raciocínio lógico foi estruturado

### 2.1 Visão geral: por que dividir em módulos

A primeira decisão de projeto foi **não escrever tudo em um único
arquivo**. Embora o desafio pudesse ser resolvido em um script único de
100–150 linhas, essa abordagem cresce mal: qualquer mudança na regra de
peso obrigaria a reler todo o arquivo para achar onde ela está aplicada,
e qualquer teste automatizado precisaria simular entrada de terminal para
testar uma regra de negócio pura.

A solução adotada separa o sistema em cinco responsabilidades isoladas,
seguindo o princípio de responsabilidade única (cada módulo tem **um
único motivo para mudar**):

| Módulo | Responsabilidade | O que muda nele |
|---|---|---|
| `models.py` | Estruturas de dados (`Peca`, `Caixa`, Enums) | Se um novo atributo de peça for exigido |
| `regras.py` | Critérios de aprovação/reprovação | Se a fábrica mudar a faixa de peso aceita |
| `estoque.py` | Orquestração (cadastro, remoção, relatório) | Se a regra de fechamento de caixa mudar |
| `persistencia.py` | Salvar/carregar estado em disco | Se o formato de armazenamento mudar (ex.: para banco de dados) |
| `main.py` | Interface de terminal (menu) | Se a forma de interação com o usuário mudar |

### 2.2 Decisões (estruturas condicionais)

A decisão central do sistema é a avaliação de qualidade
(`regras.py::avaliar_peca`). Ao invés de uma cadeia de `if/elif/else` que
interrompe na primeira condição verdadeira — abordagem comum, mas que
esconde informação —, o sistema avalia **todas as três condições
independentemente**:

```python
verificacoes = (
    avaliar_peso(peso),
    avaliar_cor(cor),
    avaliar_comprimento(comprimento),
)
motivos = tuple(m for m in verificacoes if m is not None)
aprovada = len(motivos) == 0
```

Essa escolha lógica — testar todas as condições em vez de encadear com
`elif` e parar na primeira falha — foi deliberada: uma peça que falha em
peso **e** em cor precisa reportar os dois problemas, não só o primeiro.
Do ponto de vista de quem opera a linha de produção, essa é a diferença
entre um relatório útil (que aponta a causa raiz completa) e um relatório
que obriga a testar a mesma peça repetidas vezes até descobrir todos os
defeitos.

Uma segunda decisão condicional relevante está no fechamento de caixas
(`models.py::Caixa.adicionar`): a caixa só fecha **depois** de receber a
peça que a completa, nunca antes — garantindo que a 10ª peça realmente
entre na caixa corrente, e que a 11ª abra uma nova, sem nunca ultrapassar
a capacidade:

```python
self.pecas_ids.append(peca_id)
if self.ocupacao >= self.capacidade_maxima:
    self.fechada = True
```

### 2.3 Funções

Cada regra de qualidade é isolada em sua própria função pura —
`avaliar_peso`, `avaliar_cor`, `avaliar_comprimento` — que recebe um
valor e devolve `None` (aprovado) ou uma string explicando o motivo da
reprovação. "Pura" aqui significa: a função não lê nem modifica nenhum
estado externo, e sempre devolve o mesmo resultado para a mesma entrada.
Essa propriedade é o que torna essas funções triviais de testar
isoladamente (ver `tests/test_regras.py`) e o que permite reaproveitá-las
em qualquer contexto futuro — um endpoint de API, uma esteira física,
outro protótipo — sem qualquer adaptação.

A função "guarda-chuva" `avaliar_peca` compõe as três funções atômicas
num único veredito, seguindo o princípio de composição de funções: uma
função complexa é construída a partir de funções simples e testadas
individualmente, não escrita como um bloco monolítico.

### 2.4 Condições e repetição no fluxo de armazenamento

O laço lógico "adicionar peça → caixa cheia? → fechar e abrir nova" é
implementado sem nenhum loop explícito de repetição — cada chamada a
`cadastrar_peca()` processa exatamente uma peça, e é o **próprio menu em
`main.py`** que fornece a repetição, através de um laço `while True:` que
mantém o sistema respondendo a comandos até o operador escolher `0. Sair`.

Essa separação entre "a regra de armazenamento" (sem loop, uma peça por
chamada) e "a repetição da interação com o usuário" (loop do menu) é
outra aplicação do mesmo princípio de responsabilidade única: a lógica de
armazenamento não sabe nem precisa saber que está sendo chamada dentro de
um menu interativo — poderia ser chamada 10.000 vezes em um laço `for`
processando um arquivo CSV de peças, sem qualquer alteração.

### 2.5 Tratamento de erros como parte do raciocínio lógico

Um sistema de produção real recebe entradas inesperadas: texto onde se
espera número, um id de peça repetido, uma tentativa de remover uma peça
que já foi expedida numa caixa fechada. Cada uma dessas situações foi
modelada como uma **exceção de domínio específica**
(`PecaDuplicadaError`, `PecaNaoEncontradaError`, `RemocaoBloqueadaError`)
em vez de deixar o programa quebrar com uma mensagem genérica do Python.
O menu (`main.py`) captura cada uma dessas exceções e traduz para uma
mensagem clara ao operador, sem nunca derrubar o programa — um requisito
básico de robustez para qualquer software que vá ficar rodando numa
estação de trabalho por um turno inteiro.

---

## 3. Benefícios percebidos na solução

1. **Consistência absoluta de julgamento.** Uma peça de 105.0g é sempre
   aprovada; uma de 105.1g é sempre reprovada. Não há variação entre
   operadores, turnos ou dias.
2. **Rastreabilidade completa.** Cada peça carrega o motivo exato da sua
   reprovação e a caixa exata onde foi armazenada, se aprovada — e essa
   informação persiste em disco entre execuções do programa.
3. **Feedback imediato e completo.** O operador sabe, no instante do
   cadastro, se a peça foi aprovada e por quê (ou por que não) — sem
   esperar um relatório de fim de turno.
4. **Auditabilidade do lote.** A imutabilidade das caixas fechadas
   garante que, uma vez que um lote de 10 peças é lacrado, seu conteúdo
   nunca muda silenciosamente — uma propriedade essencial para qualquer
   processo de controle de qualidade que precise responder, meses depois,
   "quais peças exatas estavam na caixa 47?".
5. **Confiabilidade comprovada por testes.** Diferente de uma planilha
   manual, cuja correção depende de revisão humana, este sistema tem 21
   testes automatizados que travam o comportamento esperado em casos de
   borda (exatamente 95g, exatamente a 10ª peça, etc.) — qualquer
   alteração futura que quebre uma regra é detectada instantaneamente.

## 4. Desafios enfrentados no desenvolvimento

1. **Definir os limites das faixas (inclusivo vs. exclusivo).** O
   enunciado do desafio diz "peso entre 95g e 105g" sem especificar se
   95g e 105g exatos são aprovados. Essa ambiguidade é comum em
   especificações reais de engenharia (por exemplo, tolerâncias
   dimensionais em normas ISO costumam tratar os limites de especificação
   como parte da faixa aceita). A decisão adotada — inclusiva — foi
   documentada explicitamente no código e neste relatório, em vez de
   resolvida silenciosamente, para que qualquer avaliador ou usuário
   futuro do sistema conheça a premissa assumida e possa alterá-la com um
   único ponto de mudança (`regras.py`).
2. **Decidir o que acontece quando se tenta remover uma peça que já está
   numa caixa fechada.** O enunciado pede a funcionalidade "remover peça
   cadastrada" sem detalhar essa regra de borda. Decidimos que caixas
   fechadas são imutáveis — espelhando a prática real de lotes lacrados —
   e implementamos essa restrição como uma exceção de domínio explícita
   (`RemocaoBloqueadaError`), em vez de permitir uma remoção "silenciosa"
   que corromperia a contagem de um lote já fechado.
3. **Garantir que a 10ª peça e a 11ª peça se comportem exatamente como
   esperado.** Esse é um clássico erro de "off-by-one" em qualquer lógica
   de agrupamento por capacidade. A solução foi escrita e depois
   validada por um teste automatizado dedicado exatamente a esse limite
   (`test_caixa_fecha_automaticamente_ao_atingir_dez_pecas` e
   `test_decima_primeira_peca_aprovada_abre_nova_caixa`), eliminando a
   necessidade de confiar apenas na leitura do código.
4. **Equilibrar simplicidade e robustez na leitura de entrada do
   terminal.** Um operador pode digitar "95,5" em vez de "95.5", ou
   deixar um campo vazio por engano. A função `ler_float()` em `main.py`
   trata essas variações (troca de vírgula por ponto, repetição da
   pergunta em caso de entrada inválida) sem exigir do operador nenhum
   conhecimento de formatação — mas isso exigiu pensar deliberadamente
   em cada forma como uma entrada real, imperfeita, poderia chegar ao
   sistema.

## 5. Reflexão final: expandindo o protótipo para um cenário real

O protótipo em Python resolve o problema em escala de demonstração — um
operador, um terminal, algumas dezenas de peças por sessão. Levá-lo a um
cenário real de produção industrial contínua exigiria evoluir três
frentes, sem necessariamente reescrever a lógica de negócio já
implementada e testada:

**Sensores substituindo a entrada manual.** Uma balança digital com
saída serial/Modbus e um sensor a laser de comprimento poderiam alimentar
`GerenciadorProducao.cadastrar_peca()` automaticamente, a cada peça que
passa por um ponto fixo da esteira — eliminando completamente a digitação
manual de peso e comprimento. A cor poderia vir de uma câmera com um
classificador simples de visão computacional (por exemplo, um modelo
leve de classificação de cor dominante via OpenCV), substituindo o
`input()` de cor por uma leitura automática em milissegundos.

**Inteligência artificial aplicada à causa raiz e à manutenção
preditiva.** O relatório atual já agrega motivos de reprovação; um passo
natural seguinte é aplicar um modelo estatístico ou de machine learning
sobre esse histórico para detectar **padrões antes que se tornem
problemas visíveis** — por exemplo, se o percentual de peças reprovadas
por "comprimento fora da faixa" começa a subir de forma consistente ao
longo de um turno, isso pode indicar desgaste de uma ferramenta de corte
muito antes que o problema afete um lote inteiro. Esse tipo de
manutenção preditiva é hoje uma das aplicações mais maduras de IA em
manufatura (Indústria 4.0).

**Integração industrial (MES/ERP e atuação física).** Num cenário real,
a decisão "reprovada" não deveria terminar num log — deveria acionar um
atuador físico (por exemplo, um desvio pneumático na esteira) que remove
automaticamente a peça defeituosa da linha principal, e o sistema
deveria se comunicar com um MES (Manufacturing Execution System) ou ERP
da fábrica para que o volume de produção, refugo e rendimento apareça em
dashboards gerenciais em tempo real, não apenas num relatório de
terminal.

O ponto que sustenta toda essa reflexão é arquitetural: como o código
já separa claramente **"como os dados chegam"** (hoje: `input()` no
terminal), **"o que é decidido"** (as regras de negócio em `regras.py`
e `estoque.py`) e **"onde os dados vão"** (hoje: um arquivo JSON e um
`print()`), cada uma dessas evoluções — sensores, IA, integração
industrial — substitui apenas as bordas do sistema. A lógica de decisão
que hoje aprova ou reprova uma peça, e que hoje fecha uma caixa ao
atingir 10 unidades, permaneceria idêntica e já validada por 21 testes
automatizados, mesmo que a peça chegasse por um sensor IoT em vez de por
um teclado.

---

## Referências

- Documentação oficial da linguagem Python: https://docs.python.org/3/
- Python Brasil — comunidade e recursos em português: https://python.org.br/
- Material da disciplina de Algoritmos e Lógica de Programação — UniFECAF.
