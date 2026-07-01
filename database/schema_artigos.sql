-- Migração: adiciona tabela de artigos ao schema existente
-- Execute este arquivo no banco já existente

CREATE TABLE IF NOT EXISTS artigos (
    id              SERIAL PRIMARY KEY,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    titulo          VARCHAR(300) NOT NULL,
    categoria       VARCHAR(100) NOT NULL DEFAULT 'Tecnologia',
    excerpt         VARCHAR(300) NOT NULL DEFAULT '',
    conteudo_markdown TEXT NOT NULL,
    read_time       VARCHAR(20) NOT NULL DEFAULT '5 min',
    data_artigo     DATE NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'gerado'
                    CHECK (status IN ('gerado', 'publicado', 'erro')),
    github_url      TEXT,
    blog_url        TEXT,
    erro            VARCHAR(500),
    criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    publicado_em    TIMESTAMP
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_artigos_status   ON artigos(status);
CREATE INDEX IF NOT EXISTS idx_artigos_slug     ON artigos(slug);
CREATE INDEX IF NOT EXISTS idx_artigos_criado   ON artigos(criado_em DESC);
