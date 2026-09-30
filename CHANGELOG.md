# Changelog

Todo lançamento notável deste projeto é documentado neste arquivo.

O formato segue o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.1.0] — 2026-09-30

### Adicionado
- **Suite de testes de integração do CLI** (`tests/test_cli.py`): 17 testes
  que simulam sessões completas de usuário (digitação, mensagens de erro,
  relatório exportado), elevando a cobertura total para **98,12%** (com 3 smoke tests da
  própria demo em `tests/test_demo.py`).
- **Testes de robustez** (`tests/test_robustez.py`): invariantes de
  `Caixa` (imutabilidade, capacidade), serialização/desserialização de
  `Peca`, e recuperação de arquivos de estado corrompidos ou inexistentes.
- **Makefile** com alvos de qualidade (`make qualidade` roda lint + tipos
  + testes — o mesmo "portão" do CI).
- **Script de demonstração automática** (`pecas_qualidade/demo.py`): roda
  um cenário completo de produção sem digitação, ideal para apresentação
  e para a gravação do vídeo pitch.
- **pyproject.toml** com configurações de `ruff`, `mypy`, `pytest` e
  `coverage` (o projeto agora é configurável pelas ferramentas padrão da
  comunidade Python).
- **CHANGELOG.md** (este arquivo).

### Alterado
- `main.py` refatorado para **injeção de dependência**:
  `executar(gerenciador=None)` permite testar o menu inteiro sem tocar no
  arquivo real de estado.
- O relatório final exportado (`relatorio_final.txt`) agora é gravado no
  diretório corrente de trabalho, não junto ao código-fonte.
- Código todo reformatado com `ruff format` e importes ordenados com
  `ruff check --fix` (estilo uniforme, 100% limpo no linter).

### Qualidade (portão de entrada do CI)
- **54 testes automatizados** (eram 21), todos passando.
- **Cobertura: 97,15%** (era 56% antes dos testes de integração).
- `pytest-cov` adicionado ao `requirements.txt` (o CI mede cobertura).
- `mypy` com `disallow_untyped_defs`, `disallow_incomplete_defs` e
  `check_untyped_defs`: **zero erros de tipagem** no pacote inteiro.
- `ruff` (pycodestyle, pyflakes, isort, bugbear, pyupgrade, simplify):
  **zero violações**.

## [1.0.0] — 2026-09-30

### Adicionado
- Versão inicial pública.
- Núcleo de regras de qualidade (`regras.py`): peso 95–105g, cor
  azul/verde, comprimento 10–20cm, com todos os motivos de reprovação
  reportados (não só o primeiro).
- Armazenamento em caixas de 10 peças com **fechamento automático** e
  **imutabilidade de caixas fechadas** (`models.py`, `estoque.py`).
- Menu interativo com as 5 operações exigidas pelo desafio (`main.py`).
- Persistência do estado em JSON entre execuções (`persistencia.py`).
- Exceções de domínio específicas (`excecoes.py`).
- 21 testes automatizados iniciais.
- Integração contínua no GitHub Actions (Python 3.10, 3.11 e 3.12).
- Documentação: `README.md`, `RELATORIO_TECNICO.md` (+ `.docx`) e
  `VIDEO_PITCH_SCRIPT.md`.
