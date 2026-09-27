# Plano de Tarefas: Aplicativo da Livraria (HTML + Flask)

Fonte única de verdade: `docs/specs/livraria.md`. Não criar regras de negócio que não estejam na spec.

- [ ] **Task 1.1 (Lógica do Domínio):** Implementar em `../../livraria.py` a classe `Livraria` e a função `criar_livraria_exemplo()`, estritamente baseadas nas User Stories US01 a US10 e nos Dados iniciais de `livraria.md`.
- [ ] **Task 1.2 (Testes):** Garantir que todos os testes de `../../tests/test_livraria.py` passem, sem alterar os testes.
- [ ] **Task 2.1 (Servidor Web):** Criar a API em `../../app.py` (Flask) expondo cada operação do domínio como rota JSON e servindo a página web. Erros de "não encontrado" retornam 404; demais erros de regra retornam 400, sempre com `{"erro": "<mensagem da spec>"}`.
- [ ] **Task 3.1 (Front-End HTML):** Criar a interface em `../../templates/index.html` consumindo a API com HTML e JavaScript, com uma área para cada módulo: busca e disponibilidade, lojas, lista de desejos e avisos, escanear e localizar, pedidos e notas fiscais.
- [ ] **Task 3.2 (Formatação):** Exibir preços no formato brasileiro (RN05).
- [ ] **Task 4.1 (Revisão):** Executar os testes, rodar a aplicação e conferir cada Critério de Aceite pela interface.