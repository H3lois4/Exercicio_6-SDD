# Especificação do Sistema – Aplicativo da Livraria

## Visão geral

Aplicativo para clientes de uma rede de livrarias físicas. O objetivo principal é
permitir que o cliente saiba, antes de sair de casa, se vale a pena ir à loja,
e que tenha uma experiência melhor dentro dela.

**Premissas**

- Não há login. O aplicativo atende um único cliente por vez (sessão única).
- Os dados ficam em memória e são carregados a partir dos **Dados iniciais** desta spec.
- O pagamento é **simulado** e sempre aprovado.
- A leitura do código de barras é simulada: o cliente digita o código (ISBN) lido.
- Toda mensagem de erro listada nesta spec deve ser exibida exatamente como escrita.

---

## Módulo 1: Consulta antes da visita (MVP)

### US01 – Consultar estoque na loja
**História de Usuário:**
Como cliente da livraria, eu quero consultar se o livro está em estoque na loja,
para não me deslocar à toa.

**Regras de negócio:**
- RN01: A busca é feita por título **ou** autor, aceita trechos e ignora maiúsculas e acentos.
- RN02: Busca com termo vazio retorna o catálogo inteiro, ordenado por título.
- RN03: A disponibilidade lista apenas as lojas que trabalham com o livro.
  O livro está **disponível** na loja quando a quantidade é maior que zero.

**Critérios de Aceite:**
```gherkin
Cenário: Livro disponível em uma loja e esgotado em outra
  Dado que o livro "Dom Casmurro" tem 3 exemplares na loja "Livraria Paulista"
  E tem 0 exemplares na loja "Livraria Pinheiros"
  Quando o cliente consulta a disponibilidade de "Dom Casmurro"
  Então o sistema deve mostrar "Livraria Paulista" como disponível com 3 exemplares
  E deve mostrar "Livraria Pinheiros" como indisponível

Cenário: Busca sem diferenciar maiúsculas e acentos
  Quando o cliente busca por "memorias postumas"
  Então o sistema deve retornar "Memórias Póstumas de Brás Cubas"

Cenário: Busca por autor
  Quando o cliente busca por "machado"
  Então o sistema deve retornar "Dom Casmurro" e "Memórias Póstumas de Brás Cubas"

Cenário: Livro inexistente
  Quando o cliente consulta a disponibilidade de um ISBN que não existe
  Então o sistema deve exibir a mensagem "Livro não encontrado"
```

### US02 – Ver o preço praticado na loja
**História de Usuário:**
Como cliente da livraria, eu quero ver o preço praticado na loja,
para não ter surpresa no caixa.

**Regras de negócio:**
- RN04: O preço é o mesmo em todas as lojas e aparece junto com a disponibilidade.
- RN05: No front-end o preço é exibido no formato brasileiro, por exemplo `R$ 1.089,00`.

**Critérios de Aceite:**
```gherkin
Cenário: Preço exibido junto com a disponibilidade
  Quando o cliente consulta a disponibilidade de "Grande Sertão: Veredas"
  Então o sistema deve informar o preço 89.00 para cada loja listada
```

### US03 – Ver horário e endereço da loja
**História de Usuário:**
Como cliente da livraria, eu quero ver o horário de funcionamento e o endereço da loja,
para planejar minha visita.

**Regras de negócio:**
- RN06: A lista de lojas é ordenada por nome.

**Critérios de Aceite:**
```gherkin
Cenário: Consultar uma loja existente
  Quando o cliente abre a loja "paulista"
  Então o sistema deve exibir o endereço "Av. Paulista, 1000 – São Paulo"
  E o horário "Seg a sáb, 10h às 22h; dom, 12h às 20h"

Cenário: Consultar uma loja inexistente
  Quando o cliente abre a loja "centro"
  Então o sistema deve exibir a mensagem "Loja não encontrada"
```

### US04 – Escolher loja favorita
**História de Usuário:**
Como cliente da livraria, eu quero escolher minha loja favorita,
para ver sempre o estoque dela primeiro.

**Regras de negócio:**
- RN07: Na disponibilidade, a loja favorita aparece primeiro; as demais seguem em ordem alfabética de nome.
- RN08: Sem loja favorita, todas seguem a ordem alfabética.

**Critérios de Aceite:**
```gherkin
Cenário: Loja favorita aparece primeiro
  Dado que o cliente escolheu "pinheiros" como loja favorita
  Quando ele consulta a disponibilidade de "A Hora da Estrela"
  Então a primeira loja exibida deve ser "Livraria Pinheiros"

Cenário: Favoritar uma loja inexistente
  Quando o cliente escolhe "centro" como loja favorita
  Então o sistema deve exibir a mensagem "Loja não encontrada"
```

---

## Módulo 2: Planejamento de compras

### US05 – Lista de desejos
**História de Usuário:**
Como cliente da livraria, eu quero salvar uma lista de desejos,
para não comprar por impulso.

**Regras de negócio:**
- RN09: A lista mantém a ordem em que os livros foram adicionados.
- RN10: Cada item mostra título, autor, preço e se está disponível em **alguma** loja.

**Critérios de Aceite:**
```gherkin
Cenário: Adicionar livro à lista de desejos
  Quando o cliente adiciona "Dom Casmurro" à lista de desejos
  Então a lista deve conter "Dom Casmurro"

Cenário: Adicionar um livro repetido
  Dado que "Dom Casmurro" já está na lista de desejos
  Quando o cliente adiciona "Dom Casmurro" novamente
  Então o sistema deve exibir a mensagem "Livro já está na lista de desejos"

Cenário: Remover livro da lista
  Dado que "Dom Casmurro" está na lista de desejos
  Quando o cliente remove "Dom Casmurro"
  Então a lista não deve conter "Dom Casmurro"

Cenário: Remover livro que não está na lista
  Quando o cliente remove um livro que não está na lista
  Então o sistema deve exibir a mensagem "Livro não está na lista de desejos"
```

### US06 – Aviso de reposição de estoque
**História de Usuário:**
Como cliente da livraria, eu quero ser avisado quando um livro esgotado voltar ao estoque,
para não checar toda semana.

**Regras de negócio:**
- RN11: Só é possível pedir aviso para um livro com quantidade zero naquela loja.
- RN12: A loja precisa trabalhar com o livro.
- RN13: Quando a quantidade passa de zero para um valor maior que zero, o sistema gera a
  notificação `O livro <título> voltou ao estoque na <nome da loja>.` e o aviso é encerrado.
- RN14: A quantidade de estoque não pode ser negativa.

**Critérios de Aceite:**
```gherkin
Cenário: Receber aviso quando o livro volta ao estoque
  Dado que "Dom Casmurro" está esgotado na "Livraria Pinheiros"
  E o cliente pediu aviso de reposição
  Quando o estoque de "Dom Casmurro" na "Livraria Pinheiros" passa para 4
  Então o cliente deve receber a notificação "O livro Dom Casmurro voltou ao estoque na Livraria Pinheiros."

Cenário: Pedir aviso de livro disponível
  Quando o cliente pede aviso de "Dom Casmurro" na "Livraria Paulista", onde há 3 exemplares
  Então o sistema deve exibir a mensagem "O livro está disponível nesta loja"

Cenário: Pedir aviso em loja que não trabalha com o livro
  Quando o cliente pede aviso de "Grande Sertão: Veredas" na "Livraria Paulista"
  Então o sistema deve exibir a mensagem "Esta loja não trabalha com este livro"

Cenário: Pedir o mesmo aviso duas vezes
  Dado que o cliente já pediu aviso de "Dom Casmurro" na "Livraria Pinheiros"
  Quando ele pede o mesmo aviso novamente
  Então o sistema deve exibir a mensagem "Aviso já cadastrado"

Cenário: Quantidade negativa
  Quando o estoque é atualizado para -1
  Então o sistema deve exibir a mensagem "Quantidade inválida"
```

---

## Módulo 3: Experiência na loja

### US07 – Escanear código de barras
**História de Usuário:**
Como cliente da livraria, eu quero escanear o código de barras na estante,
para ver sinopse e avaliações.

**Regras de negócio:**
- RN15: O código é aceito com ou sem hífens e espaços.
- RN16: A média das avaliações tem uma casa decimal. Sem avaliações, a média é vazia (nula).

**Critérios de Aceite:**
```gherkin
Cenário: Escanear livro existente
  Quando o cliente escaneia o código "978-85-359-0277-5"
  Então o sistema deve exibir a sinopse de "Dom Casmurro"
  E as avaliações com média 4.5

Cenário: Escanear código desconhecido
  Quando o cliente escaneia o código "0000000000000"
  Então o sistema deve exibir a mensagem "Livro não encontrado"
```

### US08 – Localizar o livro na estante
**História de Usuário:**
Como cliente da livraria, eu quero localizar o livro na estante pelo app,
para não precisar pedir ajuda.

**Regras de negócio:**
- RN17: A localização é composta por setor, estante e prateleira.
- RN18: Só é possível localizar livros com quantidade maior que zero na loja.

**Critérios de Aceite:**
```gherkin
Cenário: Localizar livro disponível
  Quando o cliente localiza "Dom Casmurro" na "Livraria Paulista"
  Então o sistema deve exibir setor "Literatura Brasileira", estante "4" e prateleira "2"

Cenário: Localizar livro esgotado
  Quando o cliente localiza "Dom Casmurro" na "Livraria Pinheiros"
  Então o sistema deve exibir a mensagem "Livro indisponível nesta loja"
```

### US09 – Pagar pelo app e retirar no balcão
**História de Usuário:**
Como cliente da livraria, eu quero pagar pelo app e apenas retirar no balcão,
para não enfrentar fila.

**Regras de negócio:**
- RN19: Cada pedido contém um exemplar de um livro em uma loja.
- RN20: Formas de pagamento aceitas: `pix` e `cartao`.
- RN21: Ao pagar, o estoque da loja diminui em 1 e o pedido recebe um código de retirada
  sequencial no formato `RET-0001`, com status `Aguardando retirada`.
- RN22: Na retirada, o status passa para `Retirado`. Um pedido só pode ser retirado uma vez.

**Critérios de Aceite:**
```gherkin
Cenário: Pagar pelo app
  Dado que "Dom Casmurro" tem 3 exemplares na "Livraria Paulista"
  Quando o cliente paga "Dom Casmurro" na "Livraria Paulista" com "pix"
  Então o pedido deve ter o código "RET-0001" e status "Aguardando retirada"
  E o estoque da "Livraria Paulista" deve passar para 2

Cenário: Pagar livro esgotado
  Quando o cliente paga "Dom Casmurro" na "Livraria Pinheiros"
  Então o sistema deve exibir a mensagem "Livro indisponível nesta loja"

Cenário: Forma de pagamento inválida
  Quando o cliente paga com "boleto"
  Então o sistema deve exibir a mensagem "Forma de pagamento inválida"

Cenário: Retirar no balcão
  Dado que existe o pedido "RET-0001" aguardando retirada
  Quando o balcão confirma a retirada
  Então o status do pedido deve ser "Retirado"

Cenário: Retirar duas vezes
  Dado que o pedido "RET-0001" já foi retirado
  Quando o balcão confirma a retirada novamente
  Então o sistema deve exibir a mensagem "Pedido já retirado"

Cenário: Pedido inexistente
  Quando o balcão confirma a retirada do pedido "RET-9999"
  Então o sistema deve exibir a mensagem "Pedido não encontrado"
```

### US10 – Receber a nota fiscal no app
**História de Usuário:**
Como cliente da livraria, eu quero receber a nota fiscal no app,
para não guardar papel.

**Regras de negócio:**
- RN23: Todo pagamento aprovado gera uma nota fiscal.
- RN24: A nota tem número sequencial a partir de 1, data e hora de emissão, nome da loja,
  título e ISBN do livro, forma de pagamento e valor total.
- RN25: As notas são listadas da mais recente para a mais antiga.

**Critérios de Aceite:**
```gherkin
Cenário: Nota fiscal gerada após o pagamento
  Quando o cliente paga "Dom Casmurro" na "Livraria Paulista" com "cartao"
  Então deve existir a nota fiscal número 1 com valor total 29.90

Cenário: Ordem das notas
  Dado que o cliente fez duas compras
  Quando ele abre suas notas fiscais
  Então a nota número 2 deve aparecer antes da nota número 1
```

---

## Dados iniciais

### Lojas
| id | nome | endereço | horário |
|---|---|---|---|
| paulista | Livraria Paulista | Av. Paulista, 1000 – São Paulo | Seg a sáb, 10h às 22h; dom, 12h às 20h |
| pinheiros | Livraria Pinheiros | Rua dos Pinheiros, 500 – São Paulo | Todos os dias, 9h às 21h |

### Livros
| ISBN | título | autor | preço | avaliações (nota: comentário) |
|---|---|---|---|---|
| 9788535902775 | Dom Casmurro | Machado de Assis | 29.90 | 5: Clássico indispensável. / 4: Leitura envolvente. |
| 9788571641149 | Memórias Póstumas de Brás Cubas | Machado de Assis | 34.50 | 5: Narrador genial. |
| 9788535914641 | Grande Sertão: Veredas | João Guimarães Rosa | 89.00 | 5: Obra-prima. / 3: Leitura exigente. |
| 9788501114775 | A Hora da Estrela | Clarice Lispector | 39.90 | (sem avaliações) |

### Sinopses
- **Dom Casmurro:** Bentinho relembra sua vida e o ciúme que sente de Capitu, deixando ao leitor a dúvida sobre a traição.
- **Memórias Póstumas de Brás Cubas:** Um defunto autor narra, com ironia, as memórias de uma vida sem grandes realizações.
- **Grande Sertão: Veredas:** Riobaldo, ex-jagunço, conta suas travessias pelo sertão e seu pacto com o diabo.
- **A Hora da Estrela:** A história de Macabéa, jovem nordestina que tenta sobreviver no Rio de Janeiro.

### Estoque e localização
| livro | loja | quantidade | setor | estante | prateleira |
|---|---|---|---|---|---|
| Dom Casmurro | paulista | 3 | Literatura Brasileira | 4 | 2 |
| Dom Casmurro | pinheiros | 0 | Literatura Brasileira | 2 | 1 |
| Memórias Póstumas de Brás Cubas | paulista | 0 | Literatura Brasileira | 4 | 3 |
| Grande Sertão: Veredas | pinheiros | 2 | Literatura Brasileira | 3 | 1 |
| A Hora da Estrela | paulista | 1 | Literatura Brasileira | 5 | 1 |
| A Hora da Estrela | pinheiros | 5 | Literatura Brasileira | 1 | 4 |