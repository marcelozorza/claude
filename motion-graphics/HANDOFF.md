# HANDOFF: motion graphics do vídeo "voto" (Nada Errado com VC)

Leia este arquivo e comece pelo item **Próximo passo**. Não é preciso reler a conversa anterior.

## Contexto
Vídeo de véspera de eleição para o canal Nada Errado com VC. O usuário edita no CapCut e só quer **peças de motion graphics
reutilizáveis** na estética da marca: papel quadriculado creme, recortes de papel, EB Garamond itálico, marca-texto amarelo.
Ele monta tudo manualmente. Não montar o vídeo inteiro nem entregar apresentador, legenda ou áudio, salvo pedido explícito.

## Regras do usuário
- Responder em português. Tom direto, formal, sóbrio. Sem travessão, sem ponto e vírgula, sem a fórmula "não é X, é Y".
- Confirmar antes de gastar créditos (Magnific, por exemplo) e informar o custo.
- Nada de animação "estilo JavaScript". Sem fade ou morph sem lógica física. Tudo se dobra, rasga, desliza ou cai de verdade.
- Tudo que está na tela balança poucos graus no próprio eixo, para dar sensação de papel sobre o fundo.
- Consistência de personagens e objetos importa.
- Evitar sessões longas: poucas imagens de conferência, não reler arquivos grandes, agrupar ajustes.

## O que existe (tudo em `motion-graphics/`)
| Peça | Estado | Onde |
|---|---|---|
| Papel quadriculado | aprovado | `assets/graph_paper_1080x1920.png`, `lib/fundo.py` |
| Bola de papel (entrada e saída de fotos) | aprovada | `lib/bola.py`, `lib/animfoto.py`, `lib/papel.py`, `demos/demo_bola.py` |
| Chroma key e cor do apresentador | aprovado | `lib/chroma.py` |
| Título na tela (tira de papel rasgado) | **aprovado** (entrada `'dobra'`, ritmo e linha do vinco corrigidos) | `lib/titulo.py`, `demos/demo_titulo.py`, `fonts/EBGaramond-Italic.ttf` |
| Balanço de poucos graus nos recortes | **feito, aguardando aprovação** | `balanco()` e `estado(..., fase=)` em `lib/animfoto.py`, `demos/demo_balanco.py` |
| Recortes prontos (18 figuras + logo) | prontos | `assets/recortes/` |
| Montagem completa do vídeo (referência) | rascunho | `montagem/montar.py`, `montagem/cortes_e_momentos.txt` |

`montagem/montar.py` usa caminhos relativos à pasta de trabalho original (`lib/`, `cut/`) e a fonte Helvetica Rounded Bold
da legenda, que é licenciada e **não está no repositório**. Só serve de referência de como as peças são combinadas.

## Título na tela (`lib/titulo.py`)
```python
from titulo import Titulo
t = Titulo('Lorem ipsum dolor', tempos=None, entrada='dobra')   # tempos: [(inicio, fim) por palavra], em segundos
t.quadro(seg)      # RGBA 1080x1920, seg = segundos desde a entrada
t.duracao          # entrada + leitura + saída
```
- Tira de papel rasgado (borda branca fibrosa por fora, papel creme por dentro), EB Garamond itálico peso 520.
- Uma linha até 3 palavras, duas linhas acima disso, com quebra equilibrada. Tamanho da fonte automático
  (teto 200 px em uma linha, 130 px em duas, largura máxima da tira 960 px). Referência: 1 palavra 200 px, 3 palavras 106 px,
  6 palavras 106 px, 10 palavras 66 px.
- Marca-texto amarelo (multiplicado, o texto continua escuro) avança palavra a palavra. Sem `tempos`, usa 2,6 palavras/s.
  Para uso real, passar os tempos reais da transcrição.
- **Entrada `'dobra'` (a que o usuário escolheu):** o título chega como um quadradinho de papel dobrado (cerca de metade da altura
  da tira) e se desdobra com as mesmas dobras reais da bola de papel (`TiraDobravel`, subclasse de `BolaPapel`), mostrando o verso
  branco nas dobras. A saída é o inverso e o quadradinho some. Não vira bola. Entrada 0,70 s, saída 0,60 s.
  O usuário pediu **cortar frames em vez de acelerar** (efeito stop motion), e é por isso que as durações são curtas.
- Balanço constante de cerca de 2 graus (duas senoides sobrepostas) durante entrada, leitura e saída.
- Outras entradas ainda no código, descartadas: `'desdobra'` (sanfona 2D), `'lateral'`, `'z'`, `'rasgo'`.
- Rodar o teste: `python3 demos/demo_titulo.py` (gera `demos/saida/titulo_dobra.mp4` em 540x960, exige ffmpeg e leva alguns minutos).

## Balanço nos recortes (`lib/animfoto.py`)
- `balanco(t, fase, fase2)` devolve graus. É a mesma fórmula do título (duas senoides, períodos 2,9 s e 1,7 s, cerca de 2 graus).
  O título agora chama `balanco(t, self.seed, 1.0)`, sem mudança visual.
- `estado(item, u, hold, ..., fase=0.0)` soma o balanço à rotação em todas as etapas (entrada, parada, saída, sumiço da bola).
  Recortes que ficam juntos na tela devem receber fases diferentes.
- `montagem/montar.py`: `Recorte` deriva a fase da posição (`cx`, `cy`). O cartão e a etiqueta de `Estudo` também balançam.
  O `Logo` ficou de fora porque `logo_card.png` ocupa a tela inteira (1080x1920, sem transparência) e girar mostraria as bordas.
- Mantido sem mudança: a pulsação de escala de 0,8% na parada do recorte (`sc = 1.0 + 0.008 * sin(u * 3)`). Perguntar se deve sair.
- Teste: `python3 demos/demo_balanco.py` (três recortes simultâneos, gera `demos/saida/balanco.mp4`, cerca de 50 s).
- `demos/demo_bola.py` continua quebrado fora da pasta original (importa `montar` e lê `cut/`).

## Apresentador no episódio de teste
- Recorte: `episodio-teste/saida/apresentador_recorte.png` (chroma + grade 0,26). Origem: print do vídeo dele em chroma.
- **Tamanho zero (medido sobre o print que ele mandou):** o recorte é escalado a 0,927 do tamanho nativo (largura 839 px no canvas 1080x1920),
  centralizado, topo do cabelo em y = 898 (cerca de 47% da altura), cortado pelo rodapé. A cabeça tem cerca de 266 px de largura.
- **Tamanho grande:** zero x 1,3, com o rodapé fixo (topo do cabelo em y = 592). A âncora do zoom foi suposta (rodapé), ele não confirmou.
- Cada frase muda de tamanho (zero para grande e volta), para dar ênfase e quebrar o ritmo. Ele pode ficar na frente do infográfico.
- Quadros de conferência: `episodio-teste/saida/quadro_zero.png` e `quadro_grande.png`.

## Próximo passo
**Episódio de teste em andamento.** O roteiro de 90 s está em `episodio-teste/roteiro.md` (226 palavras). O usuário vai gravar.
Com a gravação: transcrever com tempos por palavra, fazer as peças que faltam (infográfico de Hebb, citação entre aspas,
gráfico de barras), usar `Titulo(..., tempos=...)` nos dois títulos e combinar tudo sobre o vídeo dele.
O balanço nos recortes continua aguardando aprovação.

Mostrar `demos/saida/balanco.mp4` ao usuário e pedir aprovação do balanço nos recortes (amplitude e se a pulsação de escala sai).
Depois, as candidatas restantes:
1. Títulos reais: usar os tempos das palavras da transcrição no marca-texto e, se necessário, alargar a tira para cerca de 1020 px
   em títulos de 10 palavras (`largura_max`, ganha uns 10% de fonte). O tamanho do quadradinho final é o parâmetro `alvo` em `TiraDobravel.__init__`.
   Exige a transcrição com tempos por palavra.
2. Recomposição sobre o corte final dele no CapCut, renderização em alta e entrega. Exige o arquivo do corte.
   Arquivos acima de 30 MiB sobem pelo fluxo `request_upload` + PUT + `finalize_upload` do Magnific.
Registrar aqui, ao fim de cada peça aprovada, o estado novo e o próximo passo.

## Detalhes técnicos que evitam retrabalho
- Python com PIL, numpy e scipy (sem cv2 nem skimage). ffmpeg estático em `~/bin/ffmpeg`. Canvas 1080x1920 a 30 fps.
- Dobras: a folha é uma pilha de pedaços convexos. Cada dobra corta a pilha por uma reta e reflete a parte de fora (cosseno do
  ângulo no meio da dobra, verso branco além de 90 graus). Sombra com teto por pixel para não escurecer com dezenas de pedaços.
- Em `TiraDobravel` não chamar `_acabamento` da bola. Ele completa a etapa de bola e escurece a tira (ver `quadro()`).
- Renderizar quadros é lento (tira grande com dobras). Rodar em segundo plano e esperar com laço limitado, sem `pkill -f`.
