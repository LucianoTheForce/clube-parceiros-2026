# CLUBE · Parceiros 2026

Apresentação para patrocinadores e parceiros do CLUBE — bar, restaurante e pista na Rua da Consolação, 1813, São Paulo. Projeto do estúdio [The Force](https://theforce.cc).

Publicada em: https://clube-parceiros-2026.vercel.app

## Estrutura

| Caminho | O que é |
|---|---|
| `clube-apresentacao/index.html` | O deck. Um arquivo, HTML/CSS/JS puros, sem framework. 28 páginas com scroll-snap. |
| `clube-apresentacao/cotas.html` | Cotas de patrocínio 2027 (Headliner, Co-Headliner, Support): 12 páginas no mesmo sistema visual, com uma introdução curta ao CLUBE. Publicada em `/cotas.html`. |
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

PDF das cotas: copiar `cotas.html` com `<body class="pdf">` para dentro de `clube-apresentacao/`, rodar `make_pdf.py` sobre a cópia e `shrink_pdf.py` no resultado.

## Publicar

O deck está ligado ao projeto `clube-parceiros-2026` na Vercel. A partir de `clube-apresentacao/`:

```bash
vercel deploy --prod --yes
```

O arquivo `.env.local` (token da Vercel) fica fora do repositório e fora do deploy.

## Regras de conteúdo

- A casa tem **dois andares e um rooftop**: bar principal (1º), pista (2º) e rooftop.
- Tipografia apenas em Archivo; logos em branco sólido.
- Ordem do espaço sempre subindo: bar → pista → escada → rooftop.
- Inserções de marca sempre discretas; no "momento da marca", o espaço inteiro assume a cor.
