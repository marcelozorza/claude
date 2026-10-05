"""Baixa as miniaturas gratuitas do banco de vídeos do Magnific e monta folhas de contato por cena. Uso: python3 folhas.py"""
import os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont
B = 'https://videocdn.cdnpk.net/videos/'
def t(u, o='vertical'): return f'{B}{u}/{o}/thumbnails/small.jpg'
CENAS = [
 ('Cena 1a: acordando e olhando o celular', [(6396250,150,'Homem de roupão no celular', t('e4cc67c9-1515-5dc1-afa7-c7043b28c619')), (9704439,600,'Jovem acordando e vendo o celular na cama', t('609dc0cc-bf52-5918-8047-d9a5b5068af9')),
   (9697215,600,'Jovem acordando e vendo o celular na cama (mulher)', t('8d19d24a-a8ee-506a-889e-e8ccc4fa4583')), (8613124,600,'Homem reage ao celular e se levanta da cama', t('f6ed8dfe-571b-599b-9bdb-6fb2c713a847')), (6255924,600,'Mulher usando celular na cama', t('10ac7222-a9de-5bc6-ac44-91500656e753'))]),
 ('Cena 1b: sorrindo ou comemorando com o celular', [(7527310,600,'Jovem rindo para o celular', t('f01985c4-8e19-51fe-b316-8f09497b0c00')), (9688029,600,'Jovem rindo com o celular ao ar livre', t('5b282352-2402-596b-afa2-9218fe0c0f2a')),
   (6183900,600,'Mulher com celular faz gesto de vitória', t('2513ae57-1e1a-54b4-9857-184c6b27f679')), (6400637,600,'Mulher descobre algo incrível no celular', t('11d163e1-7b29-5c90-842d-a0cb1b91ee57'))]),
 ('Cenas 4, 5a e 26a: Congresso Nacional', [(9561417,600,'Esplanada dos Ministérios, vertical, vista alta', t('d36798dc-86a7-543d-803b-3b23592863b6')), (5742283,600,'Drone sobre o Congresso (horizontal)', t('17980892-4d5a-5e4e-bee7-4ef676ff9e8b','horizontal')),
   (962317,600,'Congresso, Câmara e Senado (horizontal)', t('903c42a7-9c7d-492d-b991-0c5675872d96','horizontal')), (5752090,600,'Congresso, obra de Niemeyer (horizontal)', t('6609f6ce-d586-52fa-b007-36638ee2b50f','horizontal')), (5753162,600,'Câmara dos Deputados, formato de tigela (horizontal)', t('1a5e7245-2974-5de6-ae09-10dec8960c1d','horizontal'))]),
 ('Cenas 10a e 10b: multidão diversa', [(7611048,600,'Faixa de pedestres vista de cima', t('730052d7-81e3-5b70-91b3-f40cf2ea4b48')), (6703830,600,'Cruzamento com pedestres vista de cima', t('58f64aa1-f0fa-5b09-ad07-ad8acd5b0ffe')),
   (8570939,600,'Caminhando pelas ruas de Acra', t('5337b05f-9c4d-5af4-8c2f-330866099a55')), (6653640,600,'Pessoas atravessando a rua em Kyoto, drone', t('d976316f-d32b-5aec-b7f5-a72a59ce0206'))]),
 ('Cena 13b: podcast e microfone', [(7171239,600,'Microfone de podcast em close', t('847d4043-7a23-559d-a6d2-acafaf609ce1')), (6158932,600,'Microfone de estúdio profissional', t('a1f20c95-0305-523f-9faf-8c9798bf4dd7')),
   (6650634,600,'Microfone com pop filter, luz quente', t('a3b7356b-e66b-5f77-b824-85844e64c7cb')), (7011596,600,'Microfone para podcast', t('f18b7659-f193-5ac2-86cb-8400cf1f4f97')), (5688367,600,'Microfone vintage em close', t('ef22e370-80bb-5b3c-b778-6acec94c3dee'))]),
 ('Cena 16b: sala de espera de clínica', [(4642551,600,'Sala de espera com pacientes e enfermeira', t('98c034bc-7f9b-551c-a850-aba86d50fdf8')), (7009169,600,'Pessoas na recepção de clínica', t('ba647ac9-a128-5a46-8c05-7f3e7ee6fb46')),
   (7003877,600,'Pessoas esperando em hospital', t('02323b65-48e6-5e90-9379-8ebc00db8a8f')), (7003992,600,'Idosa esperando no consultório', t('71cd6d5c-48cc-56a9-bfe8-6699024f7f61'))]),
 ('Cena 17: paciente sendo atendido', [(6871028,600,'Medição de pressão no consultório', t('21a7d41f-d280-5064-a492-58319e6880a5')), (7009806,600,'Médico idoso medindo pressão', t('0b1c15e5-9732-5e1e-a74f-7472339884d1')),
   (5122302,600,'Médico examinando as costas do paciente', t('5ab71468-9805-5ffc-8cdb-46446ee16d07')), (7009139,600,'Médica atendendo mulher no posto de saúde', t('26bd7c4e-a8dc-590a-98a3-20643de53140')), (6861187,600,'Assistente checando sinais vitais', t('d35b0762-7431-5853-ba0d-e138dc44e0af'))]),
 ('Cena 23a: terra fértil e semente', [(6679675,600,'Broto saindo da terra, ângulo baixo', t('f6e06fe1-80bc-5155-95e7-a872a6fcd100')), (7690508,600,'Timelapse de muda brotando em terra escura', t('092bc1c2-d4d6-59ea-af4c-5923d0deb3fb')),
   (6703851,600,'Broto em terra rica e texturizada', t('cda3d655-efd7-51d3-b03c-341d49aa2c7c')), (7407904,600,'Muda saindo da terra, fundo escuro', t('a6176828-b98f-5bcf-ad7c-3b6271d0ac90'))]),
]
os.makedirs('miniaturas', exist_ok=True)
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
W = 1080; TW, TH = 196, 348; GAP = 12
def thumb(vid, url):
    p = f'miniaturas/{vid}.jpg'
    if not os.path.exists(p): subprocess.run(['curl', '-sS', '-m', '30', '-o', p, url], check=True)
    return Image.open(p).convert('RGB')
folhas = [CENAS[0:3], CENAS[3:6], CENAS[6:8]]
for n, grupo in enumerate(folhas, 1):
    H = 20 + sum(60 + TH + 78 + 20 for _ in grupo); img = Image.new('RGB', (W, H), (241, 229, 201)); d = ImageDraw.Draw(img); y = 20
    for titulo, itens in grupo:
        d.text((20, y), titulo, font=F(26, True), fill=(36, 30, 26)); y += 50
        for k, (vid, custo, nome, url) in enumerate(itens):
            x = 20 + k * (TW + GAP); im = thumb(vid, url); im.thumbnail((TW, TH)); bg = Image.new('RGB', (TW, TH), (30, 26, 22)); bg.paste(im, ((TW - im.width) // 2, (TH - im.height) // 2)); img.paste(bg, (x, y))
            d.rectangle([x, y, x + 34, y + 34], fill=(255, 226, 0)); d.text((x + 9, y + 3), chr(65 + k), font=F(24, True), fill=(36, 30, 26))
            d.rectangle([x + TW - 74, y + TH - 30, x + TW, y + TH], fill=(36, 30, 26) if custo > 150 else (216, 64, 47)); d.text((x + TW - 70, y + TH - 26), f'{custo} cr', font=F(17, True), fill=(255, 255, 255))
            lin = textwrap.wrap(nome, 20)[:3]
            for j, l in enumerate(lin): d.text((x, y + TH + 4 + j * 20), l, font=F(15), fill=(36, 30, 26))
        y += TH + 78 + 10
    img.save(f'folhas/folha_{n}.png'); print('ok', n, img.size)
