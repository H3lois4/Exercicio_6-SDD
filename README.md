# Aplicativo da Livraria – SDD (Spec-Driven Development)

Aplicativo completo da livraria, desenvolvido a partir da especificação em
`docs/specs/livraria.md`, que é a fonte única de verdade do projeto.

## Artefatos

| Arquivo | Papel no SDD |
|---|---|
| `docs/specs/livraria.md` | Especificação: User Stories, regras de negócio, critérios de aceite em Gherkin e dados iniciais |
| `docs/specs/tasks.md` | Plano de tarefas executado pelo agente de IA |
| `tests/test_livraria.py` | Testes unitários derivados dos critérios de aceite |
| `livraria.py` | Lógica de domínio (US01 a US10) |
| `app.py` | API Flask que expõe o domínio e serve a página |
| `templates/index.html` | Front-end em HTML e JavaScript |

## Como rodar

```bash
pip install -r requirements.txt
pytest -v          # testes unitários
python app.py      # aplicação em http://localhost:5000
```