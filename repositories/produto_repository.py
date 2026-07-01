from sqlalchemy.orm import Session
from sqlalchemy import text


class ProdutoRepository:
    """Camada de acesso ao banco — nunca acessada diretamente pela rota"""

    def __init__(self, db: Session):
        self.db = db

    def listar_todos(self) -> list:
        resultado = self.db.execute(
            text("SELECT id, nome, descricao, preco, estoque, ativo FROM produtos WHERE ativo = TRUE ORDER BY id")
        )
        return resultado.fetchall()

    def buscar_por_id(self, produto_id: int):
        resultado = self.db.execute(
            text("SELECT id, nome, descricao, preco, estoque, ativo FROM produtos WHERE id = :id"),
            {"id": produto_id},
        )
        return resultado.fetchone()

    def criar(self, nome: str, descricao: str, preco: float, estoque: int):
        self.db.execute(
            text("""
                INSERT INTO produtos (nome, descricao, preco, estoque)
                VALUES (:nome, :descricao, :preco, :estoque)
            """),
            {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque},
        )
        self.db.commit()

    def atualizar(self, produto_id: int, nome: str, descricao: str, preco: float, estoque: int):
        self.db.execute(
            text("""
                UPDATE produtos
                SET nome = :nome, descricao = :descricao, preco = :preco,
                    estoque = :estoque, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = :id
            """),
            {"id": produto_id, "nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque},
        )
        self.db.commit()

    def deletar(self, produto_id: int):
        """Soft delete [desativar sem remover] — dado nunca é apagado fisicamente"""
        self.db.execute(
            text("UPDATE produtos SET ativo = FALSE WHERE id = :id"),
            {"id": produto_id},
        )
        self.db.commit()
