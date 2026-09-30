# Edição com chroma key e comentários

Pipeline usado no vídeo de apresentação do Nada Errado com VC (setembro de 2026).
Gera um vídeo vertical 1080x1920 com:

- chroma key do bruto da Sony, cortado na linha da cintura
- mosaico de trechos de episódios antigos rolando ao fundo, em três layouts que alternam a cada corte
- abertura com 10 comentários em pop que depois vão para o fundo
- a cada frase completa: corte, mudança de tamanho (0,85 a 1,3) e nova leva de 3 comentários na metade de cima, sem cobrir o rosto
- logo redondo em pop quando é dito "nada errado com vc"
- legendas amarelas com contorno preto, geradas da transcrição
- trilha sonora com volume automático e som de pop a cada comentário

## Dependências

- ffmpeg (a versão estática do pacote `imageio-ffmpeg` serve; os scripts chamam `~/bin/ffmpeg`)
- Python 3 com `pillow`, `numpy` e `faster-whisper`

## Pastas

Os scripts leem as variáveis de ambiente abaixo:

| Variável | Padrão | Conteúdo |
|---|---|---|
| `VIDEO_DIR` | `./trabalho/` | pasta de trabalho com `input.mp4`, `transcricao.json`, `audio/`, `clips/`, `comentarios/`, `gfx/` |
| `PRINTS_DIR` | `./prints/` | prints dos comentários do Instagram |
| `FONTS_DIR` | `./fontes/` | EB Garamond Italic (só usada por `label.py`) |

## Ordem de execução

1. `ffmpeg -i input.mp4 -vn -ac 1 -ar 16000 audio16k.wav` e depois `transcribe.py`, que gera `transcricao.json` com os tempos de cada palavra.
2. `recorta_comentarios.py`: recorta os comentários escolhidos dos prints e pixela foto e nome. As coordenadas são fixas para os prints desta edição.
3. `baixa_trechos.sh`: baixa os episódios listados em `dados/episodios.txt` pelo link público do Drive, extrai 3 trechos de 3 s de cada um e apaga o original.
4. `mosaic.py A`, `mosaic.py B` e `mosaic.py C`: geram as três variações do mosaico.
5. Editar `timeline.py`: trechos do bruto (início e fim em segundos), tamanho, fundo e comentários de cada frase.
6. `render.py --rebuild-bg`: monta o vídeo sem áudio (`gfx/video_only.mp4`). Use `--until=SEGUNDOS` para testar só o começo.
7. `audio.py`: mixa voz, trilha e pops em `gfx/mix.wav`.
8. Juntar áudio e vídeo e acelerar 10%:

```
ffmpeg -i video_only.mp4 -i mix.wav -c:v copy -c:a aac -shortest corte.mp4
ffmpeg -i corte.mp4 -filter_complex "[0:v]setpts=PTS/1.1,fps=30[v];[0:a]atempo=1.1[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 17 -c:a aac final.mp4
```

## Parâmetros que dependem da gravação

- Cor do chroma: `0x5ACD2A`, com similaridade 0.13 e mistura 0.06 (`render.py`, função `person_reader`).
- Recorte do bruto: `CROP_Y=380`, `CROP_H=1180`. A barra da camiseta fica em y≈1610 no bruto. Abaixo disso aparece a roupa de baixo, então o recorte termina em 1560.
- `HEAD_RAW=400`: altura do topo da cabeça no bruto, usada para manter os comentários fora do rosto.

## Dados desta edição

- `dados/roteiro.txt`: roteiro original
- `dados/legendas.json`: legendas finais com os tempos no vídeo antes da aceleração
- `dados/episodios.txt`: IDs do Drive e nomes dos episódios
- `dados/logo_redondo.png`: logo recortado em círculo com anel branco
