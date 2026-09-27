"""Regras de domínio do aplicativo da livraria."""

from dataclasses import dataclass, field
from datetime import datetime
import re
import unicodedata


class ErroLivraria(Exception):
	"""Erro de regra de negócio da livraria."""


class NaoEncontrado(ErroLivraria):
	"""Entidade solicitada não encontrada."""


@dataclass
class Avaliacao:
	nota: int
	comentario: str


@dataclass
class Livro:
	isbn: str
	titulo: str
	autor: str
	preco: float
	avaliacoes: list[Avaliacao] = field(default_factory=list)
	sinopse: str = ""

	@property
	def media_avaliacoes(self):
		if not self.avaliacoes:
			return None
		return round(sum(item.nota for item in self.avaliacoes) / len(self.avaliacoes), 1)


@dataclass
class Loja:
	id: str
	nome: str
	endereco: str
	horario: str


@dataclass
class Localizacao:
	setor: str
	estante: str
	prateleira: str


@dataclass
class Pedido:
	codigo_retirada: str
	status: str
	isbn: str
	titulo: str
	loja: str
	forma_pagamento: str


@dataclass
class NotaFiscal:
	numero: int
	emitida_em: datetime
	loja: str
	titulo: str
	isbn: str
	forma_pagamento: str
	total: float


def _normalizar(texto):
	sem_acentos = unicodedata.normalize("NFD", texto)
	return "".join(caractere for caractere in sem_acentos if unicodedata.category(caractere) != "Mn").casefold()


def _normalizar_isbn(isbn):
	return re.sub(r"[-\s]", "", str(isbn))


class Livraria:
	def __init__(self, livros, lojas, estoque, relogio=datetime.now):
		self._livros = {livro.isbn: livro for livro in livros}
		self._lojas = {loja.id: loja for loja in lojas}
		self._estoque = estoque
		self._relogio = relogio
		self._loja_favorita = None
		self._desejos = []
		self._avisos = set()
		self._notificacoes = []
		self._pedidos = []
		self._notas_fiscais = []

	@property
	def loja_favorita(self):
		return self._loja_favorita

	def _obter_livro(self, isbn):
		livro = self._livros.get(_normalizar_isbn(isbn))
		if livro is None:
			raise NaoEncontrado("Livro não encontrado")
		return livro

	def _obter_loja(self, loja_id):
		chave = str(loja_id).strip().casefold()
		loja = self._lojas.get(chave)
		if loja is None:
			loja = next((item for item in self._lojas.values() if item.nome.casefold() == chave), None)
		if loja is None:
			raise NaoEncontrado("Loja não encontrada")
		return loja

	def _obter_estoque(self, isbn, loja):
		item = self._estoque.get((isbn, loja.id))
		if item is None:
			raise ErroLivraria("Esta loja não trabalha com este livro")
		return item

	def buscar_livros(self, termo=""):
		consulta = _normalizar(str(termo).strip())
		livros = self._livros.values()
		if consulta:
			livros = (
				livro for livro in livros
				if consulta in _normalizar(livro.titulo) or consulta in _normalizar(livro.autor)
			)
		return sorted(livros, key=lambda livro: livro.titulo)

	def consultar_disponibilidade(self, isbn):
		livro = self._obter_livro(isbn)
		lojas = sorted(self._lojas.values(), key=lambda loja: loja.nome)
		if self._loja_favorita:
			lojas.sort(key=lambda loja: (loja.id != self._loja_favorita, loja.nome))
		resultado = []
		for loja in lojas:
			item = self._estoque.get((livro.isbn, loja.id))
			if item is not None:
				quantidade = item["quantidade"]
				resultado.append({
					"loja": loja.nome,
					"loja_id": loja.id,
					"quantidade": quantidade,
					"disponivel": quantidade > 0,
					"preco": livro.preco,
				})
		return resultado

	def listar_lojas(self):
		return sorted(self._lojas.values(), key=lambda loja: loja.nome)

	def obter_loja(self, loja_id):
		return self._obter_loja(loja_id)

	def definir_loja_favorita(self, loja_id):
		loja = self._obter_loja(loja_id)
		self._loja_favorita = loja.id
		return loja

	def adicionar_desejo(self, isbn):
		livro = self._obter_livro(isbn)
		if livro.isbn in self._desejos:
			raise ErroLivraria("Livro já está na lista de desejos")
		self._desejos.append(livro.isbn)
		return self.lista_desejos()[-1]

	def remover_desejo(self, isbn):
		livro = self._obter_livro(isbn)
		if livro.isbn not in self._desejos:
			raise ErroLivraria("Livro não está na lista de desejos")
		self._desejos.remove(livro.isbn)

	def lista_desejos(self):
		resultado = []
		for isbn in self._desejos:
			livro = self._livros[isbn]
			disponivel = any(
				item["quantidade"] > 0
				for (estoque_isbn, _), item in self._estoque.items()
				if estoque_isbn == isbn
			)
			resultado.append({
				"isbn": livro.isbn,
				"titulo": livro.titulo,
				"autor": livro.autor,
				"preco": livro.preco,
				"disponivel": disponivel,
			})
		return resultado

	def cadastrar_aviso(self, isbn, loja_id):
		livro = self._obter_livro(isbn)
		loja = self._obter_loja(loja_id)
		item = self._obter_estoque(livro.isbn, loja)
		if item["quantidade"] > 0:
			raise ErroLivraria("O livro está disponível nesta loja")
		chave = (livro.isbn, loja.id)
		if chave in self._avisos:
			raise ErroLivraria("Aviso já cadastrado")
		self._avisos.add(chave)

	def atualizar_estoque(self, isbn, loja_id, quantidade):
		if quantidade < 0:
			raise ErroLivraria("Quantidade inválida")
		livro = self._obter_livro(isbn)
		loja = self._obter_loja(loja_id)
		item = self._obter_estoque(livro.isbn, loja)
		quantidade_anterior = item["quantidade"]
		item["quantidade"] = quantidade
		chave = (livro.isbn, loja.id)
		if quantidade_anterior == 0 and quantidade > 0 and chave in self._avisos:
			self._notificacoes.append({
				"mensagem": f"O livro {livro.titulo} voltou ao estoque na {loja.nome}.",
			})
			self._avisos.remove(chave)

	def notificacoes(self):
		return list(self._notificacoes)

	def escanear_codigo(self, codigo):
		return self._obter_livro(codigo)

	def localizar_livro(self, isbn, loja_id):
		livro = self._obter_livro(isbn)
		loja = self._obter_loja(loja_id)
		item = self._obter_estoque(livro.isbn, loja)
		if item["quantidade"] == 0:
			raise ErroLivraria("Livro indisponível nesta loja")
		return item["localizacao"]

	def pagar_pedido(self, isbn, loja_id, forma_pagamento):
		livro = self._obter_livro(isbn)
		loja = self._obter_loja(loja_id)
		item = self._obter_estoque(livro.isbn, loja)
		if forma_pagamento not in ("pix", "cartao"):
			raise ErroLivraria("Forma de pagamento inválida")
		if item["quantidade"] == 0:
			raise ErroLivraria("Livro indisponível nesta loja")

		item["quantidade"] -= 1
		pedido = Pedido(
			codigo_retirada=f"RET-{len(self._pedidos) + 1:04d}",
			status="Aguardando retirada",
			isbn=livro.isbn,
			titulo=livro.titulo,
			loja=loja.nome,
			forma_pagamento=forma_pagamento,
		)
		self._pedidos.append(pedido)
		self._notas_fiscais.append(NotaFiscal(
			numero=len(self._notas_fiscais) + 1,
			emitida_em=self._relogio(),
			loja=loja.nome,
			titulo=livro.titulo,
			isbn=livro.isbn,
			forma_pagamento=forma_pagamento,
			total=livro.preco,
		))
		return pedido

	def confirmar_retirada(self, codigo_retirada):
		pedido = next(
			(item for item in self._pedidos if item.codigo_retirada == codigo_retirada),
			None,
		)
		if pedido is None:
			raise NaoEncontrado("Pedido não encontrado")
		if pedido.status == "Retirado":
			raise ErroLivraria("Pedido já retirado")
		pedido.status = "Retirado"
		return pedido

	def pedidos(self):
		return list(self._pedidos)

	def notas_fiscais(self):
		return list(reversed(self._notas_fiscais))


def criar_livraria_exemplo(relogio=datetime.now):
	lojas = [
		Loja("paulista", "Livraria Paulista", "Av. Paulista, 1000 – São Paulo", "Seg a sáb, 10h às 22h; dom, 12h às 20h"),
		Loja("pinheiros", "Livraria Pinheiros", "Rua dos Pinheiros, 500 – São Paulo", "Todos os dias, 9h às 21h"),
	]
	livros = [
		Livro("9788535902775", "Dom Casmurro", "Machado de Assis", 29.90,
			  [Avaliacao(5, "Clássico indispensável."), Avaliacao(4, "Leitura envolvente.")],
			  "Bentinho relembra sua vida e o ciúme que sente de Capitu, deixando ao leitor a dúvida sobre a traição."),
		Livro("9788571641149", "Memórias Póstumas de Brás Cubas", "Machado de Assis", 34.50,
			  [Avaliacao(5, "Narrador genial.")],
			  "Um defunto autor narra, com ironia, as memórias de uma vida sem grandes realizações."),
		Livro("9788535914641", "Grande Sertão: Veredas", "João Guimarães Rosa", 89.00,
			  [Avaliacao(5, "Obra-prima."), Avaliacao(3, "Leitura exigente.")],
			  "Riobaldo, ex-jagunço, conta suas travessias pelo sertão e seu pacto com o diabo."),
		Livro("9788501114775", "A Hora da Estrela", "Clarice Lispector", 39.90, [],
			  "A história de Macabéa, jovem nordestina que tenta sobreviver no Rio de Janeiro."),
	]
	estoque = {
		("9788535902775", "paulista"): {"quantidade": 3, "localizacao": Localizacao("Literatura Brasileira", "4", "2")},
		("9788535902775", "pinheiros"): {"quantidade": 0, "localizacao": Localizacao("Literatura Brasileira", "2", "1")},
		("9788571641149", "paulista"): {"quantidade": 0, "localizacao": Localizacao("Literatura Brasileira", "4", "3")},
		("9788535914641", "pinheiros"): {"quantidade": 2, "localizacao": Localizacao("Literatura Brasileira", "3", "1")},
		("9788501114775", "paulista"): {"quantidade": 1, "localizacao": Localizacao("Literatura Brasileira", "5", "1")},
		("9788501114775", "pinheiros"): {"quantidade": 5, "localizacao": Localizacao("Literatura Brasileira", "1", "4")},
	}
	return Livraria(livros, lojas, estoque, relogio=relogio)
