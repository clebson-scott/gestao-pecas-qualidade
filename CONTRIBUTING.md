# Contribuindo

Obrigado pelo interesse! Este é um projeto acadêmico, mas tratado com
processo profissional — as mesmas regras valem para qualquer contribuição.

## Portão de qualidade (obrigatório)

Antes de qualquer commit, rode:

```bash
make qualidade
```

Isso executa, nesta ordem:

1. **`ruff check`** — estilo e padrões propensos a bug (0 violações exigidas)
2. **`ruff format --check`** — formatação uniforme
3. **`mypy pecas_qualidade/`** — tipagem estática (0 erros exigidos)
4. **`pytest tests/`** — 51 testes, todos devem passar

O CI do GitHub Actions roda exatamente esse mesmo portão em Python 3.10,
3.11 e 3.12, com cobertura mínima exigida de **95%**. Um PR com qualquer
porta vermelha não entra.

## Regras de mudança de código

- **Regra de negócio nova ou alterada ⇒ teste novo.** Sem exceção: se você
  muda uma faixa de peso, o teste que trava a faixa antiga precisa ser
  atualizado e um novo caso de borda adicionado.
- **Bug corrigido ⇒ teste de regressão.** O teste deve falhar sem o fix e
  passar com ele.
- **Documente decisões ambíguas no código e no CHANGELOG.** Se o
  enunciado/especificação deixa algo em aberto, registre a decisão tomada —
  nunca resolva silenciosamente.
- **Mantenha as camadas separadas.** `main.py` não implementa regra de
  negócio; `regras.py` não imprime nada no terminal. Se você sente vontade
  de colocar um `input()` fora do `main.py`, pare.

## Mensagens de commit

Formato: `<tipo>: <descrição no imperativo>` — ex.: `feat: adicionar
exportação CSV do relatório`, `fix: corrigir remoção duplicando caixa`,
`test: cobrir caminho de cor vazia`.

Mudanças relevantes para quem usa o sistema entram no `CHANGELOG.md`.
