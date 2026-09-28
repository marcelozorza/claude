# Contexto do projeto Vox

Autor: Marcelo (perfil "Nada errado (com você)"). Prefere respostas em português, diretas e formais, sem travessão, sem ponto e vírgula e sem a fórmula "não é X, é Y".

## O vídeo
Ele fala para a câmera, com microfone, sobre a trend "raw dogging" (voo longo sem celular, livro, música ou água) e a rede de modo padrão (default mode network). Vertical 9:16. Ele entra e sai de infográficos e de imagens de banco. Embaixo dele há legenda com tudo o que ele fala.

## Regras de estilo (aprovadas por ele)
- Vertical 1080x1920. Gráficos só nos dois terços de cima (até y = 1280). O terço de baixo é do corpo dele.
- Estilo Vox: papel quadriculado claro, quente e uniforme (cor de areia clara), sem vinheta. Peças recortadas com sombra sobre o papel, traço de pincel feito à mão, marca-texto amarelo.
- Fonte: EB Garamond (itálico nas referências). Anotações à mão em Caveat. Números em Oswald.
- A legenda já diz tudo. Nos gráficos: sem títulos, sem nomear o que aparece, sem frases de reforço. Só a etiqueta recortada com o nome do estudo, dados (porcentagens, batimentos) e texto citado quando fizer sentido.
- Linguagem visual: os gráficos, símbolos e ícones são só os emojis 3D da Microsoft (Fluent Emoji, licença MIT), colados como adesivos com borda branca e sombra. É a peça fundamental da estética. Não usar ícones ou vetores do Magnific.
- Fotos: vêm do banco do Magnific (pode gastar à vontade) e entram como fotografias impressas jogadas sobre o papel (foto() em estilo.js): voam de fora da tela girando, derrapam e assentam inclinadas.
- Balanço de vida: tudo que entra na tela oscila alguns graus em torno do próprio centro depois de entrar (balanco() e surge() em pecas.js). Ele aprovou.
- Cérebro: emoji 3D Fluent (brain.png) ampliado, com as regiões da rede acendendo por cima (src/vox/cerebro.js). Fica macio mas bonito. Não fazer upscale.
- Composição: painéis comparativos seguem a mesma grade. Elementos soltos sem padrão incomodam.
- Cores de código (coral para rede, azul para tarefa) têm pouca importância para ele. O que importa é a informação na tela.
- Botão vermelho e interruptor foram desenhados em volume, no acabamento dos emojis, e foram aprovados.

## Som
- Efeitos discretos gerados no Magnific (pop, etiqueta, clique, choque, coração, bipe, swoosh), cortados no ataque e normalizados (public/sons/prontos). Volumes por tipo em src/vox/sons.js. Cada cena declara seus eventos em `sons`.
- O som de caneta riscando foi vetado: ele achou horrível. Não usar.
- O coração bate no ritmo exato do bpm escrito na tela.

## Cenas (código em src/vox/cenas.js e cenas2 a cenas5)
- Aprovadas antes: 08-raichle, 13-sem-botao, 19-exame (só o calendário, sem riscos nem contador, marca-texto passando pelos dias), 22a-choque-sala, 22b-choque-resultado, 29-panico, 33-dois-estados (tricô embaixo).
- Feitas depois: 01-raw-dogging, 03-rota, 04-hack, 05-telas, 07-rede, 09-vantagem, 10-defeito, 11-oficina, 12-cenarios, 15-plantar, 16-bumerangue, 17-parede, 18-e-se, 20-linha-tempo, 21-fugas, 23-pontos, 24-notificacoes, 25-porcento, 26-escala, 27-nome-estudo, 28-seta-tempo, 31-monges, 32-fera, 34-maos, 35-violino, 36-banho-louca, 38-acuado.
- Durações de 8 a 12 segundos, sem o roteiro. Ajustar ao texto dele quando ele mandar.

## Técnica
Remotion 4.0.527 com desenho em canvas 2D (30 qps). `npm install`, depois `node gera-emojis.mjs` quando entrar emoji ou foto nova. `node stills.mjs ID:segundos ...` gera quadros em out/. `node render.mjs ID ...` gera MP4 com som em out/. Renderizar em segundo plano.

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
