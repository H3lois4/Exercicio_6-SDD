from dataclasses import fields, is_dataclass
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from livraria import ErroLivraria, NaoEncontrado, criar_livraria_exemplo


app = Flask(__name__)
livraria = criar_livraria_exemplo()


def _serializar(valor):
	if is_dataclass(valor):
		return {campo.name: _serializar(getattr(valor, campo.name)) for campo in fields(valor)}
	if isinstance(valor, datetime):
		return valor.isoformat()
	if isinstance(valor, (list, tuple)):
		return [_serializar(item) for item in valor]
	if isinstance(valor, dict):
		return {chave: _serializar(item) for chave, item in valor.items()}
	return valor


@app.errorhandler(NaoEncontrado)
def tratar_nao_encontrado(erro):
	return jsonify(erro=str(erro)), 404


@app.errorhandler(ErroLivraria)
def tratar_erro_livraria(erro):
	return jsonify(erro=str(erro)), 400


@app.get("/")
def inicio():
	return render_template("index.html")


@app.get("/api/livros")
def buscar_livros():
	termo = request.args.get("q", "")
	return jsonify([_serializar(livro) for livro in livraria.buscar_livros(termo)])


@app.get("/api/livros/<isbn>")
def escanear_livro(isbn):
	return jsonify(_serializar(livraria.escanear_codigo(isbn)))


@app.get("/api/livros/<isbn>/disponibilidade")
def consultar_disponibilidade(isbn):
	return jsonify(livraria.consultar_disponibilidade(isbn))


@app.get("/api/lojas")
def listar_lojas():
	return jsonify([_serializar(loja) for loja in livraria.listar_lojas()])


@app.get("/api/lojas/<loja_id>")
def obter_loja(loja_id):
	return jsonify(_serializar(livraria.obter_loja(loja_id)))


@app.put("/api/loja-favorita")
def definir_loja_favorita():
	dados = request.get_json(silent=True) or {}
	loja = livraria.definir_loja_favorita(dados.get("loja_id", ""))
	return jsonify({"loja_favorita": loja.id})


@app.get("/api/loja-favorita")
def obter_loja_favorita():
	return jsonify({"loja_favorita": livraria.loja_favorita})


@app.route("/api/desejos", methods=["GET", "POST"])
def desejos():
	if request.method == "GET":
		return jsonify(livraria.lista_desejos())
	dados = request.get_json(silent=True) or {}
	item = livraria.adicionar_desejo(dados.get("isbn", ""))
	return jsonify(item), 201


@app.delete("/api/desejos/<isbn>")
def remover_desejo(isbn):
	livraria.remover_desejo(isbn)
	return "", 204


@app.post("/api/avisos")
def cadastrar_aviso():
	dados = request.get_json(silent=True) or {}
	livraria.cadastrar_aviso(dados.get("isbn", ""), dados.get("loja_id", ""))
	return jsonify({"cadastrado": True}), 201


@app.get("/api/notificacoes")
def notificacoes():
	return jsonify(livraria.notificacoes())


@app.put("/api/estoque")
def atualizar_estoque():
	dados = request.get_json(silent=True) or {}
	try:
		quantidade = int(dados.get("quantidade"))
	except (TypeError, ValueError):
		return jsonify(erro="Quantidade inválida"), 400
	livraria.atualizar_estoque(dados.get("isbn", ""), dados.get("loja_id", ""), quantidade)
	return jsonify({"atualizado": True})


@app.post("/api/localizacoes")
def localizar_livro():
	dados = request.get_json(silent=True) or {}
	localizacao = livraria.localizar_livro(dados.get("isbn", ""), dados.get("loja_id", ""))
	return jsonify(_serializar(localizacao))


@app.route("/api/pedidos", methods=["GET", "POST"])
def pedidos():
	if request.method == "GET":
		return jsonify([_serializar(pedido) for pedido in livraria.pedidos()])
	dados = request.get_json(silent=True) or {}
	pedido = livraria.pagar_pedido(
		dados.get("isbn", ""),
		dados.get("loja_id", ""),
		dados.get("forma_pagamento", ""),
	)
	return jsonify(_serializar(pedido)), 201


@app.post("/api/pedidos/<codigo_retirada>/retirada")
def confirmar_retirada(codigo_retirada):
	pedido = livraria.confirmar_retirada(codigo_retirada)
	return jsonify(_serializar(pedido))


@app.get("/api/notas-fiscais")
def notas_fiscais():
	return jsonify([_serializar(nota) for nota in livraria.notas_fiscais()])


if __name__ == "__main__":
	app.run(debug=True)
