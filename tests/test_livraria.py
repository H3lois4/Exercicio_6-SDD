"""Testes unitários derivados dos Critérios de Aceite de docs/specs/livraria.md."""
from datetime import datetime

import pytest

from livraria import ErroLivraria, NaoEncontrado, criar_livraria_exemplo

DOM_CASMURRO = "9788535902775"
MEMORIAS = "9788571641149"
GRANDE_SERTAO = "9788535914641"
HORA_ESTRELA = "9788501114775"


@pytest.fixture
def livraria():
    return criar_livraria_exemplo(relogio=lambda: datetime(2026, 9, 27, 14, 30))


def lojas_da_disponibilidade(livraria, isbn):
    return [item["loja"] for item in livraria.consultar_disponibilidade(isbn)]


# ---------------- US01 – Consultar estoque ----------------

class TestConsultarEstoque:
    def test_disponivel_em_uma_loja_e_esgotado_em_outra(self, livraria):
        itens = {i["loja"]: i for i in livraria.consultar_disponibilidade(DOM_CASMURRO)}
        assert itens["Livraria Paulista"]["disponivel"] is True
        assert itens["Livraria Paulista"]["quantidade"] == 3
        assert itens["Livraria Pinheiros"]["disponivel"] is False

    def test_lista_apenas_lojas_que_trabalham_com_o_livro(self, livraria):
        assert lojas_da_disponibilidade(livraria, GRANDE_SERTAO) == ["Livraria Pinheiros"]

    def test_busca_ignora_maiusculas_e_acentos(self, livraria):
        titulos = [l.titulo for l in livraria.buscar_livros("memorias postumas")]
        assert titulos == ["Memórias Póstumas de Brás Cubas"]

    def test_busca_por_autor(self, livraria):
        titulos = [l.titulo for l in livraria.buscar_livros("machado")]
        assert titulos == ["Dom Casmurro", "Memórias Póstumas de Brás Cubas"]

    def test_busca_vazia_retorna_catalogo_ordenado_por_titulo(self, livraria):
        titulos = [l.titulo for l in livraria.buscar_livros("")]
        assert titulos == sorted(titulos)
        assert len(titulos) == 4

    def test_busca_sem_resultado(self, livraria):
        assert livraria.buscar_livros("harry potter") == []

    def test_livro_inexistente(self, livraria):
        with pytest.raises(NaoEncontrado, match="Livro não encontrado"):
            livraria.consultar_disponibilidade("0000000000000")


# ---------------- US02 – Preço ----------------

class TestPreco:
    def test_preco_informado_para_cada_loja(self, livraria):
        itens = livraria.consultar_disponibilidade(GRANDE_SERTAO)
        assert all(item["preco"] == 89.00 for item in itens)


# ---------------- US03 – Horário e endereço ----------------

class TestInformacoesLoja:
    def test_loja_existente(self, livraria):
        loja = livraria.obter_loja("paulista")
        assert loja.endereco == "Av. Paulista, 1000 – São Paulo"
        assert loja.horario == "Seg a sáb, 10h às 22h; dom, 12h às 20h"

    def test_loja_inexistente(self, livraria):
        with pytest.raises(NaoEncontrado, match="Loja não encontrada"):
            livraria.obter_loja("centro")

    def test_lojas_ordenadas_por_nome(self, livraria):
        nomes = [loja.nome for loja in livraria.listar_lojas()]
        assert nomes == ["Livraria Paulista", "Livraria Pinheiros"]


# ---------------- US04 – Loja favorita ----------------

class TestLojaFavorita:
    def test_sem_favorita_ordem_alfabetica(self, livraria):
        assert lojas_da_disponibilidade(livraria, HORA_ESTRELA)[0] == "Livraria Paulista"

    def test_favorita_aparece_primeiro(self, livraria):
        livraria.definir_loja_favorita("pinheiros")
        assert lojas_da_disponibilidade(livraria, HORA_ESTRELA)[0] == "Livraria Pinheiros"
        assert livraria.loja_favorita == "pinheiros"

    def test_favoritar_loja_inexistente(self, livraria):
        with pytest.raises(NaoEncontrado, match="Loja não encontrada"):
            livraria.definir_loja_favorita("centro")


# ---------------- US05 – Lista de desejos ----------------

class TestListaDeDesejos:
    def test_adicionar(self, livraria):
        livraria.adicionar_desejo(DOM_CASMURRO)
        assert [d["titulo"] for d in livraria.lista_desejos()] == ["Dom Casmurro"]

    def test_mantem_ordem_de_inclusao_e_mostra_disponibilidade(self, livraria):
        livraria.adicionar_desejo(MEMORIAS)
        livraria.adicionar_desejo(DOM_CASMURRO)
        desejos = livraria.lista_desejos()
        assert [d["isbn"] for d in desejos] == [MEMORIAS, DOM_CASMURRO]
        assert desejos[0]["disponivel"] is False
        assert desejos[1]["disponivel"] is True
        assert desejos[1]["preco"] == 29.90

    def test_adicionar_repetido(self, livraria):
        livraria.adicionar_desejo(DOM_CASMURRO)
        with pytest.raises(ErroLivraria, match="Livro já está na lista de desejos"):
            livraria.adicionar_desejo(DOM_CASMURRO)

    def test_adicionar_livro_inexistente(self, livraria):
        with pytest.raises(NaoEncontrado, match="Livro não encontrado"):
            livraria.adicionar_desejo("0000000000000")

    def test_remover(self, livraria):
        livraria.adicionar_desejo(DOM_CASMURRO)
        livraria.remover_desejo(DOM_CASMURRO)
        assert livraria.lista_desejos() == []

    def test_remover_livro_fora_da_lista(self, livraria):
        with pytest.raises(ErroLivraria, match="Livro não está na lista de desejos"):
            livraria.remover_desejo(DOM_CASMURRO)


# ---------------- US06 – Aviso de reposição ----------------

class TestAvisoDeReposicao:
    def test_notifica_quando_volta_ao_estoque(self, livraria):
        livraria.cadastrar_aviso(DOM_CASMURRO, "pinheiros")
        livraria.atualizar_estoque(DOM_CASMURRO, "pinheiros", 4)
        mensagens = [n["mensagem"] for n in livraria.notificacoes()]
        assert mensagens == ["O livro Dom Casmurro voltou ao estoque na Livraria Pinheiros."]

    def test_aviso_e_encerrado_apos_notificar(self, livraria):
        livraria.cadastrar_aviso(DOM_CASMURRO, "pinheiros")
        livraria.atualizar_estoque(DOM_CASMURRO, "pinheiros", 4)
        livraria.atualizar_estoque(DOM_CASMURRO, "pinheiros", 0)
        livraria.atualizar_estoque(DOM_CASMURRO, "pinheiros", 2)
        assert len(livraria.notificacoes()) == 1

    def test_sem_aviso_nao_notifica(self, livraria):
        livraria.atualizar_estoque(DOM_CASMURRO, "pinheiros", 4)
        assert livraria.notificacoes() == []

    def test_aviso_de_livro_disponivel(self, livraria):
        with pytest.raises(ErroLivraria, match="O livro está disponível nesta loja"):
            livraria.cadastrar_aviso(DOM_CASMURRO, "paulista")

    def test_aviso_em_loja_que_nao_trabalha_com_o_livro(self, livraria):
        with pytest.raises(ErroLivraria, match="Esta loja não trabalha com este livro"):
            livraria.cadastrar_aviso(GRANDE_SERTAO, "paulista")

    def test_aviso_repetido(self, livraria):
        livraria.cadastrar_aviso(DOM_CASMURRO, "pinheiros")
        with pytest.raises(ErroLivraria, match="Aviso já cadastrado"):
            livraria.cadastrar_aviso(DOM_CASMURRO, "pinheiros")

    def test_quantidade_negativa(self, livraria):
        with pytest.raises(ErroLivraria, match="Quantidade inválida"):
            livraria.atualizar_estoque(DOM_CASMURRO, "paulista", -1)


# ---------------- US07 – Escanear código de barras ----------------

class TestEscanear:
    def test_codigo_com_hifens(self, livraria):
        livro = livraria.escanear_codigo("978-85-359-0277-5")
        assert livro.titulo == "Dom Casmurro"
        assert livro.sinopse.startswith("Bentinho")
        assert livro.media_avaliacoes == 4.5
        assert len(livro.avaliacoes) == 2

    def test_livro_sem_avaliacoes_tem_media_vazia(self, livraria):
        assert livraria.escanear_codigo(HORA_ESTRELA).media_avaliacoes is None

    def test_codigo_desconhecido(self, livraria):
        with pytest.raises(NaoEncontrado, match="Livro não encontrado"):
            livraria.escanear_codigo("0000000000000")


# ---------------- US08 – Localizar na estante ----------------

class TestLocalizar:
    def test_livro_disponivel(self, livraria):
        local = livraria.localizar_livro(DOM_CASMURRO, "paulista")
        assert (local.setor, local.estante, local.prateleira) == ("Literatura Brasileira", "4", "2")

    def test_livro_esgotado(self, livraria):
        with pytest.raises(ErroLivraria, match="Livro indisponível nesta loja"):
            livraria.localizar_livro(DOM_CASMURRO, "pinheiros")

    def test_loja_que_nao_trabalha_com_o_livro(self, livraria):
        with pytest.raises(ErroLivraria, match="Esta loja não trabalha com este livro"):
            livraria.localizar_livro(GRANDE_SERTAO, "paulista")


# ---------------- US09 – Pagar e retirar ----------------

class TestPagarERetirar:
    def test_pagar_pelo_app(self, livraria):
        pedido = livraria.pagar_pedido(DOM_CASMURRO, "paulista", "pix")
        assert pedido.codigo_retirada == "RET-0001"
        assert pedido.status == "Aguardando retirada"
        assert livraria.consultar_disponibilidade(DOM_CASMURRO)[0]["quantidade"] == 2

    def test_codigos_sequenciais(self, livraria):
        livraria.pagar_pedido(DOM_CASMURRO, "paulista", "pix")
        segundo = livraria.pagar_pedido(HORA_ESTRELA, "pinheiros", "cartao")
        assert segundo.codigo_retirada == "RET-0002"

    def test_pagar_livro_esgotado(self, livraria):
        with pytest.raises(ErroLivraria, match="Livro indisponível nesta loja"):
            livraria.pagar_pedido(DOM_CASMURRO, "pinheiros", "pix")

    def test_forma_de_pagamento_invalida(self, livraria):
        with pytest.raises(ErroLivraria, match="Forma de pagamento inválida"):
            livraria.pagar_pedido(DOM_CASMURRO, "paulista", "boleto")

    def test_pagamento_invalido_nao_baixa_estoque(self, livraria):
        with pytest.raises(ErroLivraria):
            livraria.pagar_pedido(DOM_CASMURRO, "paulista", "boleto")
        assert livraria.consultar_disponibilidade(DOM_CASMURRO)[0]["quantidade"] == 3

    def test_retirar_no_balcao(self, livraria):
        livraria.pagar_pedido(DOM_CASMURRO, "paulista", "pix")
        assert livraria.confirmar_retirada("RET-0001").status == "Retirado"

    def test_retirar_duas_vezes(self, livraria):
        livraria.pagar_pedido(DOM_CASMURRO, "paulista", "pix")
        livraria.confirmar_retirada("RET-0001")
        with pytest.raises(ErroLivraria, match="Pedido já retirado"):
            livraria.confirmar_retirada("RET-0001")

    def test_pedido_inexistente(self, livraria):
        with pytest.raises(NaoEncontrado, match="Pedido não encontrado"):
            livraria.confirmar_retirada("RET-9999")


# ---------------- US10 – Nota fiscal ----------------

class TestNotaFiscal:
    def test_nota_gerada_apos_pagamento(self, livraria):
        livraria.pagar_pedido(DOM_CASMURRO, "paulista", "cartao")
        nota = livraria.notas_fiscais()[0]
        assert nota.numero == 1
        assert nota.total == 29.90
        assert nota.loja == "Livraria Paulista"
        assert nota.isbn == DOM_CASMURRO
        assert nota.forma_pagamento == "cartao"
        assert nota.emitida_em == datetime(2026, 9, 27, 14, 30)

    def test_notas_da_mais_recente_para_a_mais_antiga(self, livraria):
        livraria.pagar_pedido(DOM_CASMURRO, "paulista", "pix")
        livraria.pagar_pedido(HORA_ESTRELA, "pinheiros", "pix")
        assert [n.numero for n in livraria.notas_fiscais()] == [2, 1]

    def test_pagamento_recusado_nao_gera_nota(self, livraria):
        with pytest.raises(ErroLivraria):
            livraria.pagar_pedido(DOM_CASMURRO, "pinheiros", "pix")
        assert livraria.notas_fiscais() == []