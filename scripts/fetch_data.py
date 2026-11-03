"""ETL WDI/BIS/OCDE, sem imputação. Publica snapshot completo ao concluir."""
import json,urllib.request,urllib.error,concurrent.futures,pathlib,datetime,csv,io,zipfile,hashlib,time,os
from config import COUNTRIES,INDICATORS,ISO2,START_YEAR,END_YEAR
ROOT=pathlib.Path(__file__).resolve().parents[1]
NOW=datetime.datetime.now(datetime.timezone.utc)
RETRIEVED=NOW.astimezone(datetime.timezone(datetime.timedelta(hours=-3))).date().isoformat()
RAW_OUTPUTS={}
def get(url,accept=None):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'TurquiaRelatorio/2','Accept':accept or '*/*'})
   with urllib.request.urlopen(req,timeout=90) as r:return r.read(),dict(r.headers)
  except urllib.error.HTTPError as e:
   if e.code not in [429,500,502,503,504] or n==3:raise
   time.sleep(3*(n+1))
  except (urllib.error.URLError,TimeoutError):
   if n==3:raise
   time.sleep(2**n)
def save_raw(name,raw,url,headers):
 # Não substituir respostas da edição anterior se uma fonte falhar depois.
 RAW_OUTPUTS[name]=raw
 return dict(rawFile=name,sha256=hashlib.sha256(raw).hexdigest(),url=url,retrievedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),lastModified=headers.get('Last-Modified'))
def empty_values(extra=()):return {c:{str(y):None for y in range(START_YEAR,END_YEAR+1)} for c in list(COUNTRIES)+list(extra)}
def fetch_wdi(item):
 key,(code,label,unit)=item
 url=f'https://api.worldbank.org/v2/country/{";".join(COUNTRIES)}/indicator/{code}?format=json&date={START_YEAR}:{END_YEAR}&per_page=20000'
 raw,h=get(url);provenance=save_raw(f'raw-wdi-{key}.json',raw,url,h)
 obj=json.loads(raw);assert isinstance(obj,list) and len(obj)>1,(key,obj)
 values=empty_values();flags={c:{} for c in COUNTRIES}
 for row in obj[1]:
  c=row['countryiso3code'];year=row['date'];values[c][year]=row['value']
  if row.get('obs_status'):flags[c][year]=row['obs_status']
 return key,dict(code=code,label=label,unit=unit,source='Banco Mundial · WDI',updated=obj[0].get('lastupdated'),values=values,observationStatus=flags,**provenance)
def fetch_bis():
 url='https://data.bis.org/static/bulk/WS_CBPOL_csv_flat.zip';raw,h=get(url);provenance=save_raw('raw-bis.zip',raw,url,h)
 z=zipfile.ZipFile(io.BytesIO(raw));rows=csv.DictReader(io.StringIO(z.read(z.namelist()[0]).decode('utf-8-sig')))
 months=[f'{y}-{m:02d}' for y in range(2010,int(RETRIEVED[:4])+1) for m in range(1,13) if f'{y}-{m:02d}'<=RETRIEVED[:7]]
 values={c:{month:None for month in months} for c in COUNTRIES};metadata={};flags={c:{} for c in COUNTRIES}
 for r in rows:
  c=ISO2.get(r['REF_AREA:Reference area'].split(':')[0]);date=r['TIME_PERIOD:Time period or range']
  if c and r['FREQ:Frequency'].startswith('M:') and '2010-01'<=date<=RETRIEVED[:7] and r['OBS_VALUE:Observation Value']:
   values[c][date]=float(r['OBS_VALUE:Observation Value']);flags[c][date]=r['OBS_STATUS:Observation Status']
   metadata[c]=dict(compilation=r['COMPILATION:Compilation'],source=r['SOURCE_REF:Publication Source'],breaks=r['SUPP_INFO_BREAKS:Supplemental information and breaks'])
 return 'rates',dict(label='Juros de política monetária',unit='% a.a. · fim do mês',source='BIS · bancos centrais nacionais',code='WS_CBPOL · M',values=values,metadata=metadata,observationStatus=flags,**provenance)
def fetch_hourly():
 areas='+'.join(list(COUNTRIES)+['OECD'])
 url=f'https://sdmx.oecd.org/public/rest/v1/data/OECD.SDD.TPS,DSD_PDB@DF_PDB,2.0/{areas}.A.GDPHRS._T.USD_PPP_H.LR.N..?startPeriod=2010&endPeriod=2026'
 raw,h=get(url,'text/csv;file=true');provenance=save_raw('raw-oecd-hourly.csv',raw,url,h)
 rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))));values=empty_values(['OECD']);flags={c:{} for c in values};base=set()
 for r in rows:
  c=r['REF_AREA'];year=r['TIME_PERIOD']
  assert r['MEASURE']=='GDPHRS' and r['PRICE_BASE']=='LR' and r['TRANSFORMATION']=='N'
  assert r['UNIT_MEASURE']=='USD_PPP_H' and r['ACTIVITY']=='_T'
  if c in values and year in values[c]:
   assert values[c][year] is None,'Série OCDE duplicada'
   values[c][year]=float(r['OBS_VALUE'])*10**int(r.get('UNIT_MULT') or 0) if r['OBS_VALUE'] else None
   flags[c][year]=r.get('OBS_STATUS','');base.add(r.get('BASE_PER',''))
 assert base=={'2020'},f'Base OCDE alterada: {base}; revisar rótulos'
 return 'hourly',dict(code='DSD_PDB@DF_PDB 2.0 · GDPHRS / LR / USD_PPP_H',label='PIB por hora trabalhada',unit='US$ PPC constantes de 2020 / hora',source='OCDE · Productivity Database',values=values,observationStatus=flags,basePeriod='2020',aggregate='OCDE: agregado oficial, não média simples calculada no relatório',**provenance)
def fetch_investment_breakdown():
 """Participações por ativo, somente quando numerador e total são observados."""
 areas='TUR+POL+MEX+HUN+CZE+CHL+COL+ROU'
 prefix='https://sdmx.oecd.org/public/rest/v1/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_GFCF_ASSET,1.0/'
 urls=[prefix+f'A.{areas}...P51G....XDC.V..?startPeriod=2010&endPeriod=2025',prefix+'A.TUR...P51G....XDC.V..?startPeriod=2010&endPeriod=2025']
 attempts=[]
 for i,url in enumerate(urls):
  try:
   raw,h=get(url,'text/csv;file=true');provenance=save_raw(f'raw-oecd-capital-attempt-{i}.csv',raw,url,h)
   rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
   attempts.append(dict(url=url,httpStatus=200,rows=len(rows),**{k:v for k,v in provenance.items() if k!='url'}))
   if rows:
    amounts={};statuses={}
    for row in rows:
     assert row['SECTOR']=='S1' and row['COUNTERPART_SECTOR']=='S1' and row['ACTIVITY']=='_T'
     assert row['UNIT_MEASURE']=='XDC' and row['PRICE_BASE']=='V' and row['TRANSFORMATION']=='N'
     assert row['TRANSACTION']=='P51G' and row['TABLE_IDENTIFIER']=='T0102'
     c=row['REF_AREA'];a=row['INSTR_ASSET'];y=row['TIME_PERIOD']
     if a not in ['N11G','N11MG','N111G','N112G']:continue
     key=(c,a,y);assert key not in amounts,'Duplicação em FBCF por ativo'
     amounts[key]=float(row['OBS_VALUE'])*10**int(row['UNIT_MULT']) if row['OBS_VALUE'] else None
     statuses[key]=row.get('OBS_STATUS','')
    asset_defs={'machinery_share':('N11MG','Máquinas, equipamentos e sistemas de armas'),'dwellings_share':('N111G','Habitação'),'other_buildings_share':('N112G','Outras edificações e estruturas')}
    output={};coverage={}
    for key,(asset,label) in asset_defs.items():
     values=empty_values();flags={c:{} for c in COUNTRIES};components={c:{} for c in COUNTRIES}
     for c in COUNTRIES:
      for y in values[c]:
       num=amounts.get((c,asset,y));den=amounts.get((c,'N11G',y))
       if num is not None and den is not None and den>0:
        values[c][y]=100*num/den;components[c][y]=dict(numerator=num,denominator=den,numeratorStatus=statuses[(c,asset,y)],denominatorStatus=statuses[(c,'N11G',y)])
        flags[c][y]=statuses[(c,asset,y)]+'/'+statuses[(c,'N11G',y)]
     coverage[key]={c:sorted(y for y,v in values[c].items() if v is not None) for c in COUNTRIES}
     output[key]=dict(label=label+' / FBCF',unit='% da FBCF · preços correntes',source='OCDE · contas nacionais · razão calculada',code='DF_TABLE1_EXPENDITURE_GFCF_ASSET · '+asset+'/N11G',values=values,observationStatus=flags,components=components,transformation='100 × ativo / FBCF total do mesmo país e ano, mesma moeda e preços correntes',**provenance)
    return output,dict(status='partial_coverage',attempts=attempts,coverage=coverage,fallback=['investment','manufacturing','exports'],note='Turquia: somente total N11G nesta resposta; componentes por ativo ausentes. Pares com cobertura ficam disponíveis, sem preencher a Turquia. N11MG inclui sistemas de armas; componentes apresentados não esgotam a FBCF.')
  except urllib.error.HTTPError as e:attempts.append(dict(url=url,httpStatus=e.code,retrievedAt=NOW.isoformat(),reason=str(e)))
  except (urllib.error.URLError,TimeoutError) as e:attempts.append(dict(url=url,httpStatus=None,retrievedAt=NOW.isoformat(),reason=str(e)))
 raise RuntimeError('FBCF por ativo indisponível. Nenhum snapshot ou arquivo bruto foi substituído. Tentativas: '+json.dumps(attempts,ensure_ascii=False))
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:series=dict(pool.map(fetch_wdi,INDICATORS.items()))
 key,bis=fetch_bis();series[key]=bis
 key,hourly=fetch_hourly();series[key]=hourly
 components,breakdown=fetch_investment_breakdown();series.update(components)
 completed=datetime.datetime.now(datetime.timezone.utc)
 data=dict(schemaVersion=2,retrieved=completed.astimezone(datetime.timezone(datetime.timedelta(hours=-3))).date().isoformat(),retrievedAt=completed.isoformat(),collectionStartedAt=NOW.isoformat(),timezone='America/Sao_Paulo',countries=COUNTRIES,extraAreas={'OECD':'OCDE · agregado oficial'},investmentBreakdown=breakdown,series=series)
 for name,raw in RAW_OUTPUTS.items():
  raw_tmp=ROOT/'data'/(name+'.tmp');raw_tmp.write_bytes(raw);os.replace(raw_tmp,ROOT/'data'/name)
 tmp=ROOT/'data/snapshot.json.tmp';tmp.write_text(json.dumps(data,ensure_ascii=False,allow_nan=False),encoding='utf-8');os.replace(tmp,ROOT/'data/snapshot.json')
 print('Snapshot completo:',len(series),'séries;',len(COUNTRIES),'países; consulta',RETRIEVED,flush=True)
 for k in ['investment','manufacturing','hourly']:
  print(k,{c:max((y for y,v in series[k]['values'].get(c,{}).items() if v is not None),default=None) for c in ['TUR','NGA','OECD']},flush=True)
if __name__=='__main__':main()
