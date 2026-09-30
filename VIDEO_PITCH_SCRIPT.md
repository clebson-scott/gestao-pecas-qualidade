# 🎬 Roteiro do Vídeo Pitch (até 4 minutos)

> O desafio exige um vídeo com **você** apresentando a solução — é uma
> exigência de autoria pessoal (a própria orientação diz "grave um vídeo
> apresentando SUA solução"). Por isso este roteiro é um **teleprompter
> pronto**, cronometrado e testado quanto ao tempo de fala, para você
> gravar com sua própria voz. Eu não posso gravar esse vídeo por você —
> isso precisa ser você falando, é parte do que está sendo avaliado.
>
> **Ferramenta sugerida para gravar:** [Loom](https://www.loom.com) (grava
> tela + câmera/voz simultaneamente e já gera link público em segundos —
> aceito pela orientação) ou OBS Studio + upload não-listado no YouTube.

---

## Preparação (antes de gravar)

1. Abra dois terminais lado a lado (ou uma tela cheia): um para mostrar o
   código no editor, outro para rodar `python3 -m pecas_qualidade.main`.
2. Deixe os testes já rodados numa aba (`pytest tests/ -v`) para mostrar
   o resultado verde rapidamente, sem precisar esperar a execução ao vivo.
3. Tenha pronto um cadastro de pelo menos 12 peças (10 aprovadas + 2 pra
   forçar a abertura da 2ª caixa) e 2-3 reprovadas — assim a demonstração
   ao vivo mostra o fechamento automático de caixa e os motivos de
   reprovação sem precisar digitar 20 peças na hora.

---

## Roteiro cronometrado (~3min50s de fala, com folga para os 4 minutos)

### 0:00 – 0:25 | Abertura + problema (25s)

> "Oi, eu sou o Clebson Scott, e esse é o meu trabalho de Algoritmos e
> Lógica de Programação: um sistema de gestão de peças, qualidade e
> armazenamento para uma linha de montagem industrial.
>
> O problema que resolvi é bem concreto: hoje, numa fábrica que inspeciona
> peças manualmente — com régua, balança e o olho do operador — cada
> julgamento humano varia. Isso gera atraso, erro de conferência e custo
> de operação mais alto do que precisa ser."

### 0:25 – 1:10 | Como estruturei a lógica (45s)

> "Pra resolver isso, dividi o problema em três partes lógicas.
>
> Primeiro, a avaliação: cada peça entra com id, peso, cor e comprimento,
> e passa por três verificações independentes — peso entre 95 e 105
> gramas, cor azul ou verde, comprimento entre 10 e 20 centímetros. E um
> detalhe importante: eu testo as três condições sempre, não paro na
> primeira que falhar — assim, se uma peça falha em peso E em cor, o
> relatório mostra os dois motivos, não só o primeiro.
>
> Segundo, o armazenamento: toda peça aprovada entra numa caixa de até 10
> peças. Quando a caixa enche, ela fecha automaticamente e uma nova caixa
> abre — e eu decidi que uma caixa fechada é imutável, ninguém consegue
> adicionar ou remover peça dela depois, exatamente como um lote lacrado
> numa fábrica real.
>
> Terceiro, o relatório: a qualquer momento, o sistema consolida total de
> aprovadas, total de reprovadas com o motivo de cada uma, e quantas
> caixas foram usadas."

### 1:10 – 1:35 | Técnicas e boas práticas (25s)

> "Do lado técnico, usei algumas práticas que acho que valem destacar: o
> código está separado em módulos — regras de negócio, modelos de dados,
> orquestração e interface — cada um com uma responsabilidade só. Isso
> facilita testar e facilita evoluir depois.
>
> E eu escrevi 21 testes automatizados com pytest, cobrindo até os casos
> de borda, como o que acontece exatamente na 10ª e na 11ª peça aprovada."

*(Mostre rapidamente o terminal com `pytest tests/ -v` rodando e o
resultado "21 passed" na tela — 5 a 8 segundos de tela, sem precisar
narrar tudo.)*

### 1:35 – 3:05 | Demonstração ao vivo (90s)

> "Vamos ver funcionando."

*(Rode `python3 -m pecas_qualidade.main` e narre enquanto navega:)*

> "Esse é o menu principal. Vou cadastrar uma peça dentro do padrão:
> 100 gramas, azul, 15 centímetros..."

*(Mostre a aprovação e a peça entrando na Caixa #1.)*

> "E agora uma fora do padrão, pra mostrar o motivo da reprovação..."

*(Cadastre uma peça reprovada, mostre a mensagem com os motivos.)*

> "Eu já tenho aqui um histórico de 10 peças aprovadas cadastradas antes
> da gravação — vou cadastrar mais uma pra mostrar o fechamento
> automático da caixa..."

*(Cadastre a 11ª peça aprovada e mostre que ela abre a Caixa #2. Depois
vá em "4. Listar caixas fechadas" pra mostrar a Caixa #1 fechada com 10
peças.)*

> "E por fim, o relatório final, com tudo consolidado."

*(Escolha a opção "5. Gerar relatório final" e deixe a tela visível por
alguns segundos.)*

### 3:05 – 3:50 | Encerramento + reflexão (45s)

> "Esse protótipo resolve o problema em escala de demonstração, mas ele
> foi arquitetado pra crescer sem reescrever a lógica: a mesma função que
> hoje decide se uma peça é aprovada, recebendo um número digitado no
> teclado, poderia receber esse número direto de uma balança digital ou
> de um sensor a laser — a regra de negócio não mudaria uma linha.
>
> O próximo passo natural seria visão computacional pra identificar a
> cor automaticamente por câmera, e um modelo simples de machine learning
> olhando o histórico de reprovações pra prever, por exemplo, quando uma
> ferramenta de corte está saindo de calibração — antes que ela gere um
> lote inteiro fora do padrão.
>
> O código completo, os testes e o relatório técnico estão no repositório
> do GitHub, linkado na entrega. Obrigado!"

---

## Checklist antes de enviar

- [ ] Vídeo com no máximo 4 minutos
- [ ] Mostra o problema, a lógica, as boas práticas e a demonstração ao vivo
- [ ] Link público ou não-listado (Loom / YouTube / Drive / LinkedIn)
- [ ] Link testado numa aba anônima do navegador antes de enviar (garante
      que realmente está acessível sem login)
