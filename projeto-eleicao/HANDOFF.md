# HANDOFF do projeto "eleição" (vídeo vertical 1080x1920, chroma key)

Documento interno. Não entregar ao usuário como arquivo de leitura (regra: nunca .md, só .docx ou .txt).

## Regras do usuário
- Português, tom direto, formal e sóbrio. Sem travessão, sem ponto e vírgula, sem a fórmula "não é X, é Y".
- Confirmar antes de gastar créditos do Magnific e informar o custo.
- O usuário assiste aos renders em MP4. Nada de Artifact ou página de prévia.
- Legendas: o usuário coloca sozinho, embaixo. Não adicionar legendas.
- Apresentador ocupa cerca de 60% da tela embaixo. Zoom de +30% em algumas frases.
- CROP APROVADO pelo usuário: CORTE_Y = 1288 em corte/chroma_quadro.py (medido sobre o crop que o usuário enviou). Chroma suavizado (lo=26, hi=60, miolo=2) também aprovado. Preferência: sobrar um pouco de verde a abrir buraco na camisa.
- Não rodar análises pesadas sem responder antes às mensagens do usuário.
- Highlighter nos títulos: uma passada contínua em velocidade constante. SFX de papel só nas tiras de título. Detalhes em motion-graphics/HANDOFF.md.

## Fluxo combinado
1. Cortes de falsos começos: o usuário já fez manualmente (brutoempatia.mp4 já está cortado, sem tentativas repetidas).
2. Correção de cor e chroma key (corte/chroma_quadro.py, COR 0.26). Aguarda aprovação do usuário com o crop no umbigo.
3. Versão linear sem nada aplicado para conferência.
4. Montagem seguindo projeto-eleicao/decupagem_v2.txt: algo muda na tela a cada ~5 s, motion graphics do kit (motion-graphics/lib), vídeos de apoio, fotos do Wikimedia Commons com crédito (CC BY e BY-SA exigem linha de crédito), títulos só para termos fortes.

## Arquivos do repositório
- projeto-eleicao/decupagem_v2.txt: decupagem oficial, com bloco "DECISÕES DO USUÁRIO" (carimbos direto no papel, mesmo logo redondo com pop, "continua" = imagem permanece, sem vídeo de semente, 10 vídeos de apoio).
- projeto-eleicao/roteiro.txt: roteiro de 631 palavras por linha.
- projeto-eleicao/buscar_commons.py: busca no Commons com licença e autor (User-Agent obrigatório, backoff em 429).
- projeto-eleicao/apoio/mapa_videos.txt: mapa dos 8 vídeos de apoio.
- projeto-eleicao/corte/transcrever.py: faster-whisper medium int8, pt, word_timestamps. Ainda precisa rodar para posicionar as peças em tempos reais.
- projeto-eleicao/corte/chroma_quadro.py: CLI `python3 chroma_quadro.py entrada.mp4 saida_dir t1 t2 ...`, compõe sobre fundo(1080,1920).
- motion-graphics/lib/chroma.py: key_robusto e limpa_pretos.
- edicao-chroma/dados/logo_redondo.png: logo redondo 1267x1267 RGBA, usar com pop (0,22 s) 5 vezes.
- motion-graphics/HANDOFF.md: regras e kit de motion graphics.

## Dados grandes (fora do repositório, perdidos em contêiner novo)
Baixar do Drive (arquivos compartilhados):
`curl -L -o f.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`
- Bruto já cortado: brutoempatia.mp4, id 1nWr7S2n4kKLIulZqYdVlPJ_9b8axsTaQ (salvar em /home/user/bruto/)
- Pasta de apoio: 1HsHQRmJqKU_9vBis6YDcnbHX3NNvmzXL
  - Pregnant_Hospital 1y-qY9nn1ZoY8wggOEffjpGOTtjqn93Qj
  - Cathedral_Brasilia 13bUMd0dZSRur0GoH5QW3JBdbrZGElO6X
  - Emotional_Office 1bXT_5boLONq48Bomc-k6Hd4ml2aZz9QU
  - Microphone_Studio 11mVrGKU9am74R6tl0Z2jIHH9ScYHMvRs
  - Book_Leather 1VsuLXDGlWAvDFz7nlMZT7BW2IyLyBtvE
  - Crossing_Street 1tc1OanWcRq2A4r6E-Fq2VTI8SwBXk9cg
  - People_Crowd 1PFHytmMLoJ1UhfzhERvJDkDmp8kVVvED
  - Vertical_Video_Ward 1NgtQiUs5oUP2bWjQXtmm4R8WfBG1YL-2
- C0089.MP4 (id 1drk9KcXtdJFnSEg-kAr3_DZbGv9lC4uc) está corrompido e obsoleto. Não usar.

## Decisões do usuário sobre os vídeos
- 1a e 1b: Smartphone_Bed (1920x1080, 10,36 s) enviado pelo usuário. Fora do repositório, recortar na vertical em torno das mãos. Não comprar no Magnific.
- 2: Emotional_Office em câmera lenta (0,7x).
- 3 (16b): usar Pregnant_Hospital (casal).
- Sem vídeo de semente. Sem nova lista de download.

## Estado
- Chroma e crop aprovados pelo usuário. Branch de trabalho: claude/projeto-eleicao-handoff-486ojz.
- Render completo: cerca de 5750 frames, 0,2 a 0,37 s por frame, Pool(4), 8 a 10 min. Evitar intermediários gigantes, preferir compor por frame na montagem.
- Transcrição ainda não feita.

## Armadilhas
- Nunca usar `pkill -f` ou `pgrep -f`: mata o próprio shell.
- Drive MCP baixa só arquivos pequenos. Usar curl para vídeos.
- Commons devolve 429 sem User-Agent e sem pausa.
- Magnific: busca em stock é grátis, download gasta crédito.
- Verificar números da eleição de 2026 (não confirmáveis após junho de 2026) e grafia dos títulos.

## Próximo passo
1. Baixar brutoempatia.mp4 e os vídeos de apoio.
2. Rodar chroma_quadro.py em 6 tempos com CORTE_Y=1190, enviar a imagem ao usuário e pedir aprovação do crop e da cor.
3. Rodar transcrever.py e posicionar as peças da decupagem_v2.
4. Pedir o vídeo do celular (1a/1b).
5. Renderizar versão linear e depois a montagem em MP4.
