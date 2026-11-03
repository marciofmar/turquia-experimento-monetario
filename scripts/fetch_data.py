"""Snapshot verificável WDI e BIS. Python 3, somente biblioteca padrão."""
import json, urllib.request, concurrent.futures, pathlib, datetime, csv, io, zipfile, hashlib, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
COUNTRIES={'TUR':'Turquia','BRA':'Brasil','POL':'Polônia','HUN':'Hungria','CZE':'Tchéquia','ROU':'Romênia','SRB':'Sérvia','ZAF':'África do Sul','CHL':'Chile','NGA':'Nigéria','EGY':'Egito','GHA':'Gana'}
INDICATORS={
 'gdp':('NY.GDP.MKTP.KD.ZG','Crescimento real do PIB','% ao ano'),
 'inflation':('FP.CPI.TOTL.ZG','Inflação ao consumidor','% · média anual'),
 'fx':('PA.NUS.FCRF','Câmbio oficial','moeda local por US$ · média anual'),
 'current':('BN.CAB.XOKA.GD.ZS','Conta corrente','% do PIB'),
 'productivity':('SL.GDP.PCAP.EM.KD','PIB por pessoa empregada','US$ PPC constantes de 2021'),
 'investment':('NE.GDI.FTOT.ZS','Formação bruta de capital fixo','% do PIB'),
 'hightech':('TX.VAL.TECH.MF.ZS','Exportações de alta tecnologia','% das exportações de manufaturados'),
 'manufacturing':('NV.IND.MANF.ZS','Valor adicionado da indústria de transformação','% do PIB'),
 'rd':('GB.XPD.RSDV.GD.ZS','Pesquisa e desenvolvimento','% do PIB'),
 'income':('NY.GDP.PCAP.KD','PIB real por habitante','US$ constantes de 2015')}
def get(url):
 for n in range(4):
  try:
   with urllib.request.urlopen(url,timeout=90) as r:return r.read()
  except Exception:
   if n==3:raise
   time.sleep(2**n)
def fetch(item):
 key,(code,label,unit)=item
 url=f'https://api.worldbank.org/v2/country/{";".join(COUNTRIES)}/indicator/{code}?format=json&date=2010:2026&per_page=20000'
 raw=get(url); (ROOT/'data'/f'raw-wdi-{key}.json').write_bytes(raw)
 obj=json.loads(raw); assert isinstance(obj,list) and len(obj)>1,(key,obj)
 values={c:{} for c in COUNTRIES}
 for row in obj[1]:values[row['countryiso3code']][row['date']]=row['value']
 return key,dict(code=code,label=label,unit=unit,url=url,source='Banco Mundial · WDI',updated=obj[0].get('lastupdated'),sha256=hashlib.sha256(raw).hexdigest(),values=values)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: series=dict(pool.map(fetch,INDICATORS.items()))
 url='https://data.bis.org/static/bulk/WS_CBPOL_csv_flat.zip'
 raw=get(url); (ROOT/'data'/'raw-bis.zip').write_bytes(raw)
 z=zipfile.ZipFile(io.BytesIO(raw)); print('BIS files',z.namelist())
 text=z.read(z.namelist()[0]).decode('utf-8-sig'); rows=list(csv.DictReader(io.StringIO(text))); print('BIS columns',list(rows[0]),'sample',rows[0])
 (ROOT/'data'/'bis-rows.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
 data=dict(retrieved='2026-11-02',countries=COUNTRIES,series=series,bisSource=url,bisSha256=hashlib.sha256(raw).hexdigest())
 (ROOT/'data'/'snapshot.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
 print('WDI cobertura', {k:{c:max((y for y,v in s['values'][c].items() if v is not None),default=None) for c in ['TUR','BRA','POL']} for k,s in series.items()})
