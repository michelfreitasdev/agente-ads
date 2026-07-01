"""
github_service.py — Publicação de artigos via GitHub API

Responsabilidade única: criar ou atualizar o arquivo .md
no repositório do blog, disparando o deploy automático.
"""

import os
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_REPO = os.getenv("GITHUB_REPO") or (
    f"{GITHUB_OWNER}/{GITHUB_REPOSITORY}" if GITHUB_OWNER and GITHUB_REPOSITORY else "AdminFreitas/digitaltech"
)
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")


def _headers() -> dict:
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN não configurado")

    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _url_arquivo(slug: str) -> str:
    return f"https://api.github.com/repos/{GITHUB_REPO}/contents/content/artigos/{slug}.md"


def publicar_artigo(slug: str, conteudo_markdown: str, titulo: str) -> dict:
    """
    Cria o arquivo .md no repositório do blog.
    Se o arquivo já existir, atualiza o conteúdo.
    Retorna a URL do arquivo no GitHub.
    """
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN não configurado")

    url = _url_arquivo(slug)
    conteudo_b64 = base64.b64encode(conteudo_markdown.encode("utf-8")).decode("utf-8")
    headers = _headers()

    # Verifica se o arquivo já existe (para pegar o SHA necessário no update)
    sha = None
    with httpx.Client(timeout=15.0) as client:
        resp = client.get(url, headers=headers)
        if resp.status_code == 200:
            sha = resp.json().get("sha")

    payload = {
        "message": f"feat: adiciona artigo '{titulo}'",
        "content": conteudo_b64,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    with httpx.Client(timeout=15.0) as client:
        resp = client.put(url, headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Erro ao publicar no GitHub: {resp.status_code} — {resp.text}")

    html_url = resp.json().get("content", {}).get("html_url", "")
    return {
        "github_url": html_url,
        "blog_url": f"https://digitaltech.digital/artigos/{slug}",
        "atualizado": sha is not None,
    }


def artigo_existe(slug: str) -> bool:
    """Verifica se um artigo com este slug já existe no repositório."""
    if not GITHUB_TOKEN:
        return False

    with httpx.Client(timeout=10.0) as client:
        resp = client.get(_url_arquivo(slug), headers=_headers())
    return resp.status_code == 200
