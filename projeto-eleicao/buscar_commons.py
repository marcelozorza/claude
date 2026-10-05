"""Busca imagens no Wikimedia Commons com licença e autor. Uso: python3 buscar_commons.py "termo" ["termo2" ...]  (imprime título, tamanho, licença, autor, link)"""
import sys, json, re, html, time, urllib.parse, urllib.request, urllib.error
UA = {'User-Agent': 'Mozilla/5.0 (pesquisa-imagens-video; uso editorial)'}
def api(**p):
    p['format'] = 'json'; url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p)
    for k in range(6):
        try: time.sleep(1.2); return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(6 * (k + 1))
    raise RuntimeError('Commons recusou (429) várias vezes')
def limpar(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s or ''))).strip()
def buscar(termo, n=6):
    r = api(action='query', list='search', srsearch=termo + ' filetype:bitmap', srnamespace=6, srlimit=n)
    titulos = [x['title'] for x in r['query']['search']]
    if not titulos: return []
    d = api(action='query', titles='|'.join(titulos), prop='imageinfo', iiprop='url|size|mime|extmetadata', iiurlwidth=640)
    out = []
    for p in d['query']['pages'].values():
        ii = (p.get('imageinfo') or [{}])[0]; em = ii.get('extmetadata', {})
        out.append({'titulo': p['title'], 'w': ii.get('width'), 'h': ii.get('height'), 'licenca': limpar(em.get('LicenseShortName', {}).get('value')),
                    'autor': limpar(em.get('Artist', {}).get('value'))[:60], 'data': limpar(em.get('DateTimeOriginal', {}).get('value'))[:20],
                    'pagina': 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(p['title'].replace(' ', '_')), 'miniatura': ii.get('thumburl'), 'url': ii.get('url')})
    return out
if __name__ == '__main__':
    for t in sys.argv[1:]:
        print('\n== ', t)
        for o in buscar(t): print(f"  {o['titulo'][5:70]:65s} {o['w']}x{o['h']}  {o['licenca']:14s} {o['autor']}")
