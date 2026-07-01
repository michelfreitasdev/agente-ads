"""
gemini_service.py — Geração de artigos com Google Gemini

Responsabilidade única: receber um tema e devolver
um artigo completo em Markdown com frontmatter.
"""

import os
import re
import json
import unicodedata
from datetime import date
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def _gerar_slug(titulo: str) -> str:
    """Converte título em slug URL-friendly."""
    slug = titulo.lower()
    slug = unicodedata.normalize("NFD", slug)
    slug = slug.encode("ascii", "ignore").decode("utf-8")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug[:80]


def gerar_artigo(tema: str, categoria: str = "Tecnologia") -> dict:
    """
    Recebe um tema e retorna dicionário com:
    - slug, titulo, categoria, excerpt
    - conteudo_markdown (frontmatter + corpo)
    - data
    """
    model = genai.GenerativeModel(MODEL)

    prompt = f"""Você é um escritor técnico brasileiro especializado em tecnologia.

Escreva um artigo completo em Markdown sobre o tema: "{tema}"
Categoria: {categoria}

REGRAS OBRIGATÓRIAS:
1. Escreva APENAS em português brasileiro
2. Tom profissional mas acessível
3. Entre 500 e 800 palavras no corpo do artigo
4. Use exemplos de código quando relevante (blocos ```linguagem)
5. Estruture com ## para seções principais e ### para subseções
6. Termine com uma conclusão prática

FORMATO DE SAÍDA — responda EXATAMENTE neste formato JSON:
{{
  "titulo": "Título do artigo aqui",
  "excerpt": "Resumo de uma linha (máx 120 caracteres)",
  "readTime": "X min",
  "corpo": "## Primeira seção\\n\\nConteúdo aqui..."
}}

Responda APENAS com o JSON, sem texto antes ou depois."""

    resposta = model.generate_content(prompt)
    texto = resposta.text.strip()
    texto = re.sub(r"^```json\n?", "", texto)
    texto = re.sub(r"\n?```$", "", texto)

    dados = json.loads(texto)
    slug = _gerar_slug(dados["titulo"])
    hoje = date.today().isoformat()

    conteudo_markdown = f"""---
slug: {slug}
title: "{dados['titulo']}"
category: {categoria}
excerpt: "{dados['excerpt']}"
date: {hoje}
readTime: {dados['readTime']}
published: true
---

{dados['corpo']}
"""

    return {
        "slug": slug,
        "titulo": dados["titulo"],
        "categoria": categoria,
        "excerpt": dados["excerpt"],
        "readTime": dados["readTime"],
        "conteudo_markdown": conteudo_markdown,
        "data": hoje,
    }
