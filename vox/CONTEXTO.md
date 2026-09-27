# Contexto do projeto Vox

Autor: Marcelo (perfil "Nada errado (com você)"). Prefere respostas em português, diretas e formais, sem travessão, sem ponto e vírgula e sem a fórmula "não é X, é Y".

## O vídeo
Ele fala para a câmera, com microfone, sobre a trend "raw dogging" (voo longo sem celular, livro, música ou água) e a rede de modo padrão (default mode network). Vertical 9:16. Ele entra e sai de infográficos e de imagens de banco. Embaixo dele há legenda com tudo o que ele fala.

## Regras de estilo (aprovadas por ele)
- Vertical 1080x1920. Gráficos só nos dois terços de cima (até y = 1280). O terço de baixo é do corpo dele.
- Estilo Vox: papel quadriculado claro, quente e uniforme (cor de areia clara), sem vinheta, sem cara de velho. Peças recortadas com sombra sobre o papel, traço de pincel feito à mão, marca-texto amarelo.
- Fonte: EB Garamond (itálico nas referências). Anotações à mão em Caveat. Números em Oswald.
- A legenda já diz tudo. Nos gráficos: sem títulos, sem nomear o que aparece, sem frases de reforço. Só a etiqueta recortada com o nome do estudo (ele adorou esse detalhe), dados (porcentagens, batimentos) e texto citado quando fizer sentido.
- Imagens: emojis 3D da Microsoft (Fluent Emoji, licença MIT, raw.githubusercontent.com/microsoft/fluentui-emoji) aplicados como adesivos com borda branca e sombra. Ele gostou muito.
- Desenhos feitos à mão em código ficam fracos (ele criticou o cérebro). Preferir assets de qualidade: emojis 3D, fotos e ilustrações de banco. Este chat novo tem acesso ao Magnific e à internet, então buscar assets de verdade.
- Botão vermelho e interruptor foram desenhados em volume (gradientes), no acabamento dos emojis. O relógio é emoji.
- Cérebro: emoji 3D Fluent (brain.png, 256 px) ampliado, com as regiões da rede acendendo por cima (src/vox/cerebro.js). Ele aprovou: fica macio mas bonito. Não fazer upscale.
- Composição: painéis comparativos seguem a mesma grade (situação à esquerda, cérebro no meio, coração e bpm à direita, ECG embaixo). Ele reclamou de elementos soltos sem padrão.
- Cores de código (coral para rede, azul para tarefa) têm pouca importância para ele. O que importa é a informação na tela.
- Pode gastar créditos do Magnific baixando assets.

## Cenas feitas (código em src/vox/cenas.js)
- 08-raichle: cérebro (emoji 3D) parado, regiões da rede de modo padrão acendendo, etiqueta "Raichle et al., 2001 · PNAS".
- 13-sem-botao: cérebro (emoji 3D) com a rede acesa e interruptor que desliga e volta sozinho.
- 19-exame: semana SEG a SEX, riscos de contagem das voltas ao assunto, contador, "informação nova: 0" que vira 1 na sexta.
- 22a-choque-sala: relógio (15 min) e botão vermelho, etiqueta "Wilson et al., 2014 · Science". Aprovada.
- 22b-choque-resultado: barras 67% homens (12 de 18) e 25% mulheres (6 de 24). Aprovada.
- 29-panico: ciclo de seis etapas com bolinha acelerando e coração 3D batendo mais rápido.
- 33-dois-estados: dois painéis na mesma grade. Em cima: avião, cérebro com a rede acesa, coração 132 bpm, ECG coral. Embaixo: tricô (yarn), cérebro calmo, coração 66 bpm, ECG azul. Aprovada.

## Próximo passo combinado
Cenas 8, 13 e 33 já trocadas para o cérebro emoji e renderizadas. Próximo: ele escolhe as próximas cenas da lista abaixo. Mandar prévia parada antes de renderizar.

## Checagem científica já passada a ele
- Estudo do choque: 25% das mulheres (6 de 24), não 27%. 67% dos homens (12 de 18).
- Killingsworth e Gilbert, 2010 ("A wandering mind is an unhappy mind"): 2.250 pessoas; mente vagando 46,9% do tempo; menos felizes em média (não "100% das vezes"); o estudo mede mente vagando, não a rede de modo padrão; a análise temporal mostra mente vagando antes da infelicidade (não ansiedade e depressão clínicas).
- Raichle 2001: regiões específicas mais ativas no repouso e que desligam na tarefa; "acendeu todo" exagera.
- Monges (Brewer 2011): menos atividade na rede durante a meditação; "por isso mais felizes" não é demonstrado.
- Einstein e o violino: relato de terceiros ("contam que").
- Pânico: adrenalina e noradrenalina aceleram em segundos; cortisol vem depois.
- Haaland: não verificado.

## Lista completa de cenas sugeridas (uma por parágrafo do roteiro)
1 raw dogging: ícones se apagando sobre passageiro [imagem]. 3 Haaland: vídeo dele + rota de voo. 4 "hack secreto": cadeado brilhante irônico. 5 "telas destruíram a rede": rachaduras e carimbo "?". 7 a rede existe: regiões acendendo. 8 Raichle (feita). 9 vantagem evolutiva. 10 defeito evolutivo. 11 cabeça vazia, oficina. 12 galhos de cenários. 13 sem botão de desligar (feita). 15 plantar, prever, resolver andando. 16 bumerangue. 17 galhos batendo na parede. 18 luto e "e se" [imagem]. 19 exame de sexta (feita). 20 linha do tempo de milênios com celular no fim. 21 álcool, sexo, violência [imagem]. 22 choque (feita, em duas). 23 2.250 pontos. 24 notificações do app. 25 47%. 26 escala de felicidade. 27 nome do estudo. 28 seta temporal. 29 ciclo do pânico (feita). 31 monges. 32 fera domada. 33 dois estados (feita). 34 mãos ocupadas [imagem]. 35 Einstein e o violino. 36 banho, louça [imagem]. 38 bicho acuado.

## Técnica
Remotion 4.0.527 com desenho em canvas 2D (30 qps). Scripts: `node still.mjs ID segundos` gera um quadro em out/; `node render.mjs ID ...` gera MP4 em out/. Renderizar vídeos em segundo plano (demoram vários minutos). O Chromium usado fica em /opt/pw-browsers/chromium_headless_shell-*/.
