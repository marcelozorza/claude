# HANDOFF do projeto "eleição" e das animações de infográfico (atualizado em 6 de outubro de 2026)

Documento interno. Não entregar ao usuário como arquivo. Regra do usuário: nunca entregar .md, só .txt ou .docx.

## Como começar numa sessão nova na nuvem
1. Mude para a branch de trabalho: `git fetch origin claude/projeto-eleicao-handoff-486ojz` e `git checkout claude/projeto-eleicao-handoff-486ojz`. A branch padrão do remoto (claude/magnific-resource-search-x7f2iy) NÃO tem esta pasta. O usuário autorizou trabalhar e dar push em claude/projeto-eleicao-handoff-486ojz.
2. Dependências: python3 com pillow, numpy e scipy (`pip install pillow numpy scipy`), ffmpeg e uma fonte DejaVu. A fonte EB Garamond itálico está em motion-graphics/fonts.
3. O usuário está num PC com After Effects, mas esta sessão roda na nuvem e NÃO alcança o PC. O trabalho no After Effects acontece numa sessão local separada (ver "After Effects" abaixo).

## Regras do usuário (consolidadas)
Idioma e tom
- Português, tom direto, formal e sóbrio. Sem travessão, sem ponto e vírgula, sem a fórmula "não é X, é Y".
- Confirmar antes de gastar créditos do Magnific e informar o custo.
- O usuário assiste aos renders em MP4. Nada de Artifact ou página de prévia. Arquivos acima de uns 25 MB não sobem: dividir.
Processo
- Ir mais devagar. 1 a 3 cenas por vez, cada uma em arquivo próprio, com o NÚMERO DA CENA no nome. Sempre dizer o número ao entregar. O usuário corrige apontando só o número (exemplo: I2 quadro 4).
- Antes de renderizar, fazer um STORYBOARD DESENHADO da cena (quadros em sequência, só número e tempo). Descrição escrita confunde o usuário.
- Nunca mais gerar o vídeo inteiro montado. Só cenas separadas, o que vai atrás do apresentador. O usuário monta tudo no editor. Sem legendas e sem sobrepor o apresentador.
Estilo
- Fundo sempre o papel pautado (motion-graphics/assets/graph_paper_1080x1920.png, lib/fundo.py). Tipografia EB Garamond itálico. Marca-texto amarelo que passa uma vez em velocidade constante.
- Paleta: creme #F1E5C9, tinta #241E1A, amarelo #FFE200, vermelho #CC2228 (só ênfase), azul #5696B0, terracota #E27A5C, verde #6EAA70.
- DESENHO: pictogramas no estilo ISO 7001 (exercício aceito para os storyboards). Formas chapadas, cor sólida, SEM contorno, SEM borda branca, SEM sombra. Figura humana = cabeça redonda e barras arredondadas (montagem/pictogramas.py). O estilo anterior, com borda branca de papel e sombra, foi considerado feio.
- Não desenhar objetos complicados (urna e martelo ficaram ruins). Preferir formas simples, tipografia e fotos reais licenciadas do Commons com crédito (projeto-eleicao/creditos.txt). Nunca inventar o rosto de uma pessoa real. Nunca usar modelo de vídeo de IA.
- NUNCA escrever na tela texto que narre ou explique o infográfico. A imagem se explica sozinha. Os títulos do roteiro o usuário coloca na edição.
- FAIXA DE CIMA PROIBIDA: nada nos 15% de cima do quadro (y < 288 em 1920), por causa da interface do Instagram. Vale para arte, títulos, sombra e bolinha em voo. Embaixo pode, porque o apresentador ocupa cerca de 60% da tela embaixo. O gerador mede e RECUSA gerar se passar disso (bola_cena.topo_minimo).
- Movimento: tudo balança poucos graus no próprio eixo. Lógica física, sem fade nem morph. Preferir stop motion (cortar quadros) a acelerar.
Estrutura padrão de cada cena (12,4 s)
- A bolinha de papel chega em arco balístico (0,60 s), abre (0,55 s), ficam 10 s de arte com balanço leve (sempre 10 s, nunca parada), fecha em bolinha (0,55 s) e vai embora pelo mesmo arco (0,60 s), mais 0,1 s de folga. Nada de outra cena na tela durante a abertura ou o fechamento. Gerar a mais, o usuário corta e nunca estica.
- BOLA APROVADA, não mexer mais: placas grandes e irregulares, branco neutro, sem linhas pretas finas. Um degrau de bola menor e mais apertada na entrada e na saída, desenhada de novo (nunca redimensionada). A bola do simulador de dobras troca para a bola desenhada com corte seco aos 93% do fechamento.

## O que existe no repositório
- motion-graphics/lib/bola.py (BolaPapel, bola_realista, estagios_amassados), bola_cena.py (CicloBola, topo_minimo), animfoto.py, papel.py, titulo.py (tira de papel, entrada 'dobra'), fundo.py, chroma.py.
- projeto-eleicao/montagem/cena.py (Cena = CicloBola em volta de uma lista de peças), gerar_cenas.py (`python3 gerar_cenas.py <id> <escala> <pasta>` gera um MP4 por cena, e `--quadros t1,t2 <pasta>` gera quadros avulsos em segundos GLOBAIS, onde a arte começa em 1,15 s), cenas_def.py (registro das cenas), pecas.py, infograficos.py (cenas 22c, 22d e 23 no estilo ANTIGO com borda de papel, obsoletas).
- projeto-eleicao/montagem/pictogramas.py (formas chapadas: pessoa, coração, flecha, nuvem, disco, retângulo, linha), storyboards_picto.py (quadros-chave de I1 a I5 em pictograma, funções i1 a i5 e folha()), storyboards.py (estilo antigo), folha.py (junta quadros jpg em uma grade).
- projeto-eleicao/storyboards/*_pictograma.png (os storyboards atuais) e os antigos sem sufixo.
- projeto-eleicao/prompt_estilo.txt: prompt de estilo para colar numa sessão nova (usado na sessão local do After Effects).
- Montagem inteira abandonada, mas o código fica: montar_eleicao.py e corte/chroma_quadro.py (chroma e crop aprovados, CORTE_Y 1288, âncora CX 462), transcricao.json, decupagem_v2.txt, roteiro.txt.

## VÍDEO ANTERIOR (05/10, 19:07), EM PAUSA: os cinco infográficos I1 a I5
Só retomar se o usuário pedir. Numerados na ordem do roteiro. Todos sem texto na tela.
- I1 As duas dores que vêm depois: uma flecha acerta o peito do boneco (inevitável), duas outras partem antes de chegar e caem.
- I2 O humor pinta os pensamentos: nuvens claras em volta do boneco ficam cinza, se soltam e vão embora.
- I3 Respirar com a expiração mais longa: círculo cresce rápido e encolhe devagar, onda de subida curta e descida longa, duas barras (curta amarela, longa azul).
- I4 Não há volta, só para cima: ladrilhos desabam atrás do boneco e degraus sobem à frente, ele sobe.
- I5 O pequeno que continua: curva vermelha de fúria dispara e despenca, linha azul fina segue, cartazes de papel formam uma SETA para cima (nunca uma cruz).
Estado: storyboards em pictograma enviados ao usuário, SEM resposta ainda. Sugestão de primeira rodada: I1, I3 e I4.

## Perguntas em aberto do vídeo anterior (só retomar se o usuário pedir)
1. Quais storyboards em pictograma aprova, o que muda, e por quais cenas começar.
2. A bolinha de papel (com borda branca e fibras) ainda faz sentido com peças sem borda, ou prefere outra transição para esse estilo?
3. O limite de cima é 15% (y 288), como combinado, ou chega a 20% (y 384)? Usado 15%.
4. Estilo chapado vale também para as cenas animadas (hoje só valeu nos storyboards).

## After Effects (sessão local, fora da nuvem)
- O usuário testa After Effects com MCP no PC. Painel instalado: "MCP Bridge Auto" (TheLlamainator/after-effects-mcp, comunicação por arquivos em Documents\ae-mcp-bridge: ae_command.json e ae_mcp_result.json). Esse MCP não documenta preview nem render. Alternativas: LiamcKerr/after-effects-mcp (tem ae_preview_frame, só local) e aftr (renderiza e confere os quadros).
- Esta sessão na nuvem não alcança o PC. A sessão local (Claude Desktop ou `claude remote-control`) usa projeto-eleicao/prompt_estilo.txt. As duas sessões compartilham o repositório: fazer pull antes de push e não editar os mesmos arquivos.
- Avaliado e NÃO adotado: JohnHeibel/ClaudeAnimationBase (p5.js e p5.brush, 40 s por quadro sem GPU, estilo de tinta e aquarela, mascote Clawd). Ideias aproveitáveis: princípios de animação (antecipação, sobra de movimento, suavização, peso) e a folha de leituras por cena. O usuário não aprovou aplicá-las.

## Próximo passo
O usuário vai começar um VÍDEO NOVO. Não há tarefa de construção pendente.
1. Perguntar o que o usuário traz: roteiro, tema e data. Não assumir nada do vídeo anterior.
2. Com o roteiro, propor os trechos que mais rendem infográfico. Critérios que funcionaram: o trecho tem uma metáfora visual clara, dá para desenhar com formas simples (pictograma chapado, sem texto na tela) e a imagem ajuda mais do que a fala sozinha. Numerar na ordem do roteiro. Sugestão: usar o prefixo do vídeo no número (por exemplo V2_I1) para não confundir com I1 a I5 do vídeo anterior.
3. Antes de construir, mostrar um STORYBOARD DESENHADO de cada infográfico (montagem/storyboards_picto.py serve de modelo) e esperar a aprovação.
4. Construir 1 a 3 cenas por vez, com o kit em Python e a estrutura de cena de 12,4 s, MP4 em 540p, dizendo o número de cada uma. Seguir todas as regras acima, incluindo a faixa de cima proibida e nada de texto narrando.
5. Registrar neste arquivo o que o usuário aprovar.

## Armadilhas
- Nunca usar `pkill -f` ou `pgrep -f`: mata o próprio shell. Sem `sleep` em primeiro plano: usar run_in_background com laço until.
- `from modulo import *` não traz nomes que começam com sublinhado (ex.: _bola). Importar explicitamente.
- Erro no inicializador de um multiprocessing.Pool faz os processos reiniciarem para sempre sem mensagem. Testar montar() fora do Pool.
- Wikimedia Commons devolve 429 sem User-Agent e sem pausa. Miniaturas em tamanhos padrão (500px funciona).
- Magnific: busca em stock é grátis, download e geração gastam crédito.
- Verificar números da eleição de 2026 e grafia dos títulos. Não citar pesquisa nem número que não esteja no roteiro.

## Arquivo (dados da montagem abandonada, fora do repositório)
Vídeo bruto cortado: brutoempatia.mp4, Drive id 1nWr7S2n4kKLIulZqYdVlPJ_9b8axsTaQ. Pasta de apoio: 1HsHQRmJqKU_9vBis6YDcnbHX3NNvmzXL (Pregnant_Hospital 1y-qY9nn1ZoY8wggOEffjpGOTtjqn93Qj, Cathedral_Brasilia 13bUMd0dZSRur0GoH5QW3JBdbrZGElO6X, Emotional_Office 1bXT_5boLONq48Bomc-k6Hd4ml2aZz9QU, Microphone_Studio 11mVrGKU9am74R6tl0Z2jIHH9ScYHMvRs, Book_Leather 1VsuLXDGlWAvDFz7nlMZT7BW2IyLyBtvE, Crossing_Street 1tc1OanWcRq2A4r6E-Fq2VTI8SwBXk9cg, People_Crowd 1PFHytmMLoJ1UhfzhERvJDkDmp8kVVvED, Vertical_Video_Ward 1NgtQiUs5oUP2bWjQXtmm4R8WfBG1YL-2). Download: `curl -L -o f.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`. Smartphone_Bed foi enviado pelo usuário e não está no Drive.
