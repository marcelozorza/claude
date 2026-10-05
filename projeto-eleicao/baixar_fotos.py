"""Baixa as fotos escolhidas do Wikimedia Commons (largura 1600) e escreve creditos.txt. Uso: python3 baixar_fotos.py pasta_saida"""
import sys, os, time, urllib.parse, urllib.request
UA = {'User-Agent': 'Mozilla/5.0 (pesquisa-imagens-video; uso editorial)'}
FOTOS = [  # nome, arquivo no Commons, autor, licença
 ('camara', 'Plenário da Câmara dos Deputados (17028665114).jpg', 'MDB Nacional', 'CC BY 2.0'),
 ('constituicao', 'Promulgação-Constituição-1988.jpg', 'Agência Brasil', 'CC BY 3.0 br'),
 ('senado', 'Plenário do Senado (24790862386).jpg', 'Senado Federal', 'CC BY 2.0'),
 ('urna', 'Urna eletrônica brasileira UE2020.jpg', 'TSE', 'Domínio público'),
 ('congresso', 'Fachada do Congresso Nacional (48079560916).jpg', 'Senado Federal', 'CC BY 2.0'),
 ('musk', 'Elon Musk (2025) (cropped).jpg', 'U.S. Secretary of Defense', 'Domínio público'),
 ('rogan', 'Joerogan.png', 'Rebecca Lai (corte: East718)', 'CC BY 2.0')]
if __name__ == '__main__':
    pasta = sys.argv[1]; os.makedirs(pasta, exist_ok=True); linhas = []
    for nome, arq, autor, lic in FOTOS:
        url = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(arq) + '?width=1600'
        for k in range(6):
            try:
                time.sleep(1.5); d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
                ext = '.png' if arq.lower().endswith('.png') else '.jpg'; open(os.path.join(pasta, nome + ext), 'wb').write(d); print(nome, len(d)); break
            except Exception as e: print(nome, 'tentativa', k, e); time.sleep(6 * (k + 1))
        linhas.append(f'{nome}: "{arq}", {autor}, {lic}, Wikimedia Commons (commons.wikimedia.org/wiki/File:{arq.replace(" ", "_")})')
    open(os.path.join(pasta, 'creditos.txt'), 'w').write('CRÉDITOS DAS FOTOS\n' + '\n'.join(linhas) + '\n')
