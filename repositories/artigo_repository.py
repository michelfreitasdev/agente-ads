"""
artigo_repository.py — Acesso ao banco de dados para artigos

Registra todos os artigos gerados e publicados,
com histórico de status para rastreabilidade.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date


class ArtigoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(
        self,
        slug: str,
        titulo: str,
        categoria: str,
        excerpt: str,
        conteudo_markdown: str,
        read_time: str,
        data_artigo: str,
    ) -> int:
        """Salva artigo gerado com status 'gerado'. Retorna o ID."""
        resultado = self.db.execute(
            text("""
                INSERT INTO artigos
                    (slug, titulo, categoria, excerpt, conteudo_markdown, read_time, data_artigo, status)
                VALUES
                    (:slug, :titulo, :categoria, :excerpt, :conteudo, :read_time, :data_artigo, 'gerado')
                RETURNING id
            """),
            {
                "slug": slug,
                "titulo": titulo,
                "categoria": categoria,
                "excerpt": excerpt,
                "conteudo": conteudo_markdown,
                "read_time": read_time,
                "data_artigo": data_artigo,
            },
        )
        self.db.commit()
        return resultado.fetchone()[0]

    def marcar_publicado(self, artigo_id: int, github_url: str, blog_url: str) -> None:
        """Atualiza status para 'publicado' após deploy no GitHub."""
        self.db.execute(
            text("""
                UPDATE artigos
                SET status = 'publicado',
                    github_url = :github_url,
                    blog_url = :blog_url,
                    publicado_em = NOW()
                WHERE id = :id
            """),
            {"id": artigo_id, "github_url": github_url, "blog_url": blog_url},
        )
        self.db.commit()

    def marcar_erro(self, artigo_id: int, erro: str) -> None:
        """Registra erro durante a publicação."""
        self.db.execute(
            text("UPDATE artigos SET status = 'erro', erro = :erro WHERE id = :id"),
            {"id": artigo_id, "erro": erro[:500]},
        )
        self.db.commit()

    def buscar_por_id(self, artigo_id: int):
        return self.db.execute(
            text("SELECT * FROM artigos WHERE id = :id"),
            {"id": artigo_id},
        ).fetchone()

    def listar_todos(self, limite: int = 50):
        return self.db.execute(
            text("""
                SELECT id, slug, titulo, categoria, status, data_artigo, publicado_em
                FROM artigos
                ORDER BY criado_em DESC
                LIMIT :limite
            """),
            {"limite": limite},
        ).fetchall()

    def buscar_por_slug(self, slug: str):
        return self.db.execute(
            text("SELECT * FROM artigos WHERE slug = :slug"),
            {"slug": slug},
        ).fetchone()
