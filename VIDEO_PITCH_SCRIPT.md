# 🎬 Roteiro do Vídeo Pitch — versão curta (2min30s)

> **Por que essa versão:** roteiro enxuto para não estourar os 4 minutos.
> Fala total: ~300 palavras. Com pausas naturais, dá 2min20s a 2min40s —
> sobra margem de segurança.
>
> **Roteiro adaptado (PCD auditivo):** as legendas na tela carregam metade
> da apresentação. Se em algum trecho você preferir não falar, deixe a
> legenda sozinha na tela por 3 segundos — o conteúdo continua completo.
> Ferramentas com legenda automática em português: **Loom** (legenda nativa),
> **CapCut** (PC, gratuito) ou **YouTube** (upload e correção manual).
>
> **Regra de ouro:** legendas SEMPRE ligadas. Elas garantem que a banca
> entenda tudo, servem de apoio pra você, e mostram cuidado com
> acessibilidade — ninguém vai tirar nota por isso, pelo contrário.

---

## Preparação (5 minutos, antes de gravar)

1. Dois terminais abertos, lado a lado:
   - Esquerda: no VS Code, arquivo `pecas_qualidade/regras.py` visível.
   - Direita: pronto pra digitar `make demo`.
2. Já ter rodado `pytest tests/ -q` uma vez (para o estado existir — a demo
   usa arquivo temporário, então não precisa).
3. Legenda automática LIGADA na ferramenta de gravação.
4. Fale 10% mais devagar do que o normal. Vídeo curto dá esse luxo.

---

## Roteiro cronometrado

### 0:00 – 0:20 | Abertura + problema (legenda: seu nome + disciplina)

> "Oi, eu sou Clebson Scott. Este é meu trabalho de Algoritmos e Lógica
> de Programação: um sistema de gestão de peças, qualidade e
> armazenamento pra linha de montagem industrial.
>
> O problema: inspeção manual com régua e balança varia de operador pra
> operador. Gera erro, atraso e custo."

*(13 segundos de fala. Legenda na tela: "Inspeção manual → erro, atraso,
custo".)*

### 0:20 – 0:50 | A lógica em 3 partes (legenda: 1, 2, 3 na tela)

> "Dividi a lógica em três partes.
>
> Primeira: avaliação. Cada peça passa por três checagens — peso entre
> 95 e 105 gramas, cor azul ou verde, comprimento entre 10 e 20
> centímetros. Testo as três sempre: a peça reprovada recebe TODOS os
> motivos, não só o primeiro.
>
> Segunda: armazenamento. Aprovada entra numa caixa de até 10 peças. Caixa
> cheia fecha sozinha e fica imutável — como lote lacrado.
>
> Terceira: relatório consolidado, com motivos de reprovação e uso das
> caixas."

*(30 segundos. Na tela, mostre `regras.py` no editor enquanto fala.)*

### 0:50 – 1:05 | Boas práticas (legenda: os números)

> "No código: módulos separados por responsabilidade, tipagem estática,
> e 54 testes automatizados com cobertura de 98 por cento. A integração
> contínua roda tudo a cada alteração."

*(15 segundos. Se quiser, encaixe 2 segundos do terminal com
`54 passed` na tela — opcional.)*

### 1:05 – 2:00 | Demonstração (legenda: o que a tela mostra)

> "Agora, o sistema rodando. Preparei uma demonstração automática com 15
> peças."

*(Digite `make demo` e ESPERE em silêncio — a demo se auto-explica na
tela, é proposital. Apenas aponte com o mouse enquanto ela roda.)*

*(Na seção [3/4] da demo, a tentativa de remoção na caixa fechada:)*

> "Regra de negócio viva: caixa fechada é imutável. O sistema bloqueia."

*(No relatório final da demo, 3 segundos de silêncio com a tela parada.)*

> "Relatório consolidado: taxa de aprovação, cada motivo de reprovação,
> caixas usadas."

*(55 segundos no total — a tela trabalha, você fala só ~40 palavras.)*

### 2:00 – 2:25 | Reflexão (legenda: "próximos passos")

> "A função que aprova a peça recebe o número do teclado hoje — mas
> poderia receber da balança digital ou sensor a laser, sem mudar uma
> linha. É a separação entre regra de negócio e interface que permite
> isso.
>
> Próximo passo natural: câmera com visão computacional pra identificar
> a cor."

*(25 segundos.)*

### 2:25 – 2:30 | Encerramento (legenda: link do GitHub)

> "Código, testes e relatório técnico estão no GitHub, linkado na
> entrega. Obrigado!"

*(5 segundos. Mostre a aba do repositório com o badge verde do CI.)*

---

## Checklist antes de enviar

- [ ] Vídeo entre 2min20s e 2min40s (limite do desafio: 4 min)
- [ ] Legendas corretas (revisar o texto gerado automaticamente —
      principalmente os números: 95, 105, 10, 20, 98%)
- [ ] Os 4 blocos exigidos aparecem: problema, lógica, boas práticas,
      demonstração ao vivo (a demo automática conta como demonstração —
      mostra o sistema executando de ponta a ponta, com relatório)
- [ ] Sua presença: nome falado e legenda na abertura (autoria)
- [ ] Link público ou não-listado (Loom / YouTube / Drive)
- [ ] Link testado numa aba anônima antes de enviar

---

## Plano B: se estourar o tempo na 1ª gravação

Corte, nesta ordem, sem perder nota:
1. A frase da integração contínua ("a integração contínua roda tudo")
   — o badge verde na aba final já mostra isso.
2. O detalhe "como lote lacrado" da parte de armazenamento.
3. A pausa de 3 segundos do relatório (reduza pra 2).

**Não corte nunca:** os três critérios numéricos (95/105, azul/verde,
10/20), os motivos de reprovação completos, a imutabilidade da caixa
fechada, e o encerramento com o GitHub. São os itens que a banca procura.
