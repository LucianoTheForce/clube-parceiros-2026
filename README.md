# CLUBE · Parceiros 2026

Apresentação para patrocinadores e parceiros do CLUBE — bar, restaurante e pista na Rua da Consolação, 1813, São Paulo. Projeto do estúdio [The Force](https://theforce.cc).

Publicada em: https://clube-parceiros-2026.vercel.app

## Estrutura

| Caminho | O que é |
|---|---|
| `clube-apresentacao/index.html` | O deck de parceiros 2027: intro curta do espaço (24h, sala imersiva, LED da pista, galeria digital, hotel), clube de membros, app e Rádio CLUBE, Instagram e PR, e as cotas de patrocínio (Headliner, Co-Headliner, Support). Um arquivo, HTML/CSS/JS puros, sem framework. 23 páginas com scroll-snap. O app aparece num slide com o app ao vivo (`clube-blond.vercel.app/clube`) num iPhone; a Rádio CLUBE toca na barra do topo, com a playlist do app. Slideshows com autoplay. Só as cotas: tag `v2-cotas-fotos-tratadas`. |
| `clube-apresentacao/assets/` | Imagens (WebP), vídeos (MP4), fontes (Archivo em WOFF2) e texturas do cartão. |
| `clube-apresentacao/vercel.json` | Cabeçalhos de publicação (`noindex`, cache dos assets). |
| `build-assets/` | Versões leves dos vídeos, usadas apenas na exportação de arquivo único. |
| `build.py` | Gera as três exportações a partir do deck (ver abaixo). |
| `make_pdf.py` · `shrink_pdf.py` | Exportação em PDF, uma página por slide, via Chrome headless + DevTools. |
| `snap_slide.py` | Captura de um slide em tamanho exato (para conferência visual). |

## Rodar localmente

Qualquer servidor estático serve. Por exemplo:

```bash
python -m http.server 8765 --directory clube-apresentacao
```

e abrir http://localhost:8765.

## Exportações

```bash
python build.py
```

Gera na raiz:

- `CLUBE-parceiros-2026.html` — arquivo único com tudo embutido (link, com animações);
- `clube-apresentacao-artifact.html` — corpo da página para publicação como artifact;
- `CLUBE-parceiros-2026-PDF.html` — versão congelada, uma página por slide, sem vídeo;
- `CLUBE-parceiros-2026-pasta.zip` — a pasta do deck, sem credenciais.

Para o PDF: `python make_pdf.py CLUBE-parceiros-2026-PDF.html _raw.pdf` e depois `python shrink_pdf.py`.

## Publicar

O deck está ligado ao projeto `clube-parceiros-2026` na Vercel. A partir de `clube-apresentacao/`:

```bash
vercel deploy --prod --yes
```

O arquivo `.env.local` (token da Vercel) fica fora do repositório e fora do deploy.

## Regras de conteúdo

- A casa tem 8 andares (térreo = 1º): bar e restaurante (1º), hotel (2º ao 6º), pista e bar com vista (7º), rooftop (8º), mais a sala imersiva. Aberta 24 horas (café, mesa, aperitivo, noite).
- Fotos só das originais do espaço (sem IA), tratadas sem mudar arquitetura, piso nem móveis; ver `fotos-tratadas/` fora do repo.
- Tipografia apenas em Archivo; logos em branco sólido.
- Ordem do espaço sempre subindo: bar → pista → escada → rooftop.
- Inserções de marca sempre discretas; no "momento da marca", o espaço inteiro assume a cor.
