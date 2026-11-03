"""Validação independente das fontes, transformações e propriedades do estimador."""
import json,pathlib,hashlib,math,csv,io,zipfile,copy,datetime
import numpy as np
from analyze import calculate,solve,matrices
from config import PRINCIPAL,ISO2
import fetch_data
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/snapshot.json').read_text(encoding='utf-8'))
A=json.loads((ROOT/'data/analysis.json').read_text(encoding='utf-8'))
checks=0
def check(condition,message):
 global checks
 if not condition:raise AssertionError(message)
 checks+=1
def close(x,y,tol=1e-8):return x is None and y is None or x is not None and y is not None and abs(x-y)<tol
# A etapa de download deve poder falhar sem sobrescrever uma edição existente.
probe_name='validation-staging-probe.txt'
fetch_data.save_raw(probe_name,b'fixture','https://example.invalid',{})
check(not (ROOT/'data'/probe_name).exists(),'ETL escreveu resposta antes de concluir coleta')
check(fetch_data.RAW_OUTPUTS.pop(probe_name)==b'fixture','Buffer transacional divergente')
check(A['metadata']['snapshotSha256']==hashlib.sha256((ROOT/'data/snapshot.json').read_bytes()).hexdigest(),'Snapshot mudou após análise')
for f,h in A['metadata']['codeSha256'].items():check(hashlib.sha256((ROOT/'scripts'/f).read_bytes()).hexdigest()==h,'Código da análise divergente: '+f)
embedded=json.loads((ROOT/'data/data.js').read_text(encoding='utf-8').removeprefix('window.REPORT_DATA=').removesuffix(';'))
check(embedded['synthetic']==A,'Análise do navegador divergente')
copy_embedded=copy.deepcopy(embedded);del copy_embedded['synthetic'];check(copy_embedded==D,'Snapshot do navegador divergente')
for key,s in D['series'].items():
 check(hashlib.sha256((ROOT/'data'/s['rawFile']).read_bytes()).hexdigest()==s['sha256'],'Hash bruto: '+key)
 check(s['retrievedAt']<=D['retrievedAt'],'Consulta de fonte posterior ao fechamento')
 for c,values in s['values'].items():
  check(all(v is None or isinstance(v,(int,float)) and math.isfinite(v) for v in values.values()),'Valor inválido '+key+'/'+c)
 if s['source']=='Banco Mundial · WDI':
  raw=json.loads((ROOT/'data'/s['rawFile']).read_text(encoding='utf-8'))
  for row in raw[1]:check(s['values'][row['countryiso3code']][row['date']]==row['value'],'Divergência WDI '+key)
 if 'components' in s:
  raw=list(csv.DictReader(io.StringIO((ROOT/'data'/s['rawFile']).read_text(encoding='utf-8-sig'))))
  asset={'machinery_share':'N11MG','dwellings_share':'N111G','other_buildings_share':'N112G'}[key]
  observed={(r['REF_AREA'],r['INSTR_ASSET'],r['TIME_PERIOD']):float(r['OBS_VALUE'])*10**int(r['UNIT_MULT']) for r in raw if r['OBS_VALUE']}
  for c,years in s['values'].items():
   for y,v in years.items():
    num=observed.get((c,asset,y));den=observed.get((c,'N11G',y))
    expected=100*num/den if num is not None and den is not None and den>0 else None
    check(close(v,expected),'Componente imputado ou razão incorreta')
    if v is not None:check(0<=v<=100,'Parcela de ativo fora do intervalo')
# Juros e produtividade por hora conferidos contra respostas originais.
rate=D['series']['rates'];z=zipfile.ZipFile(ROOT/'data/raw-bis.zip');rawrates=csv.DictReader(io.StringIO(z.read(z.namelist()[0]).decode('utf-8-sig')))
rate_rows=0
for r in rawrates:
 c=ISO2.get(r['REF_AREA:Reference area'].split(':')[0]);y=r['TIME_PERIOD:Time period or range']
 if c and r['FREQ:Frequency'].startswith('M:') and y in rate['values'][c] and r['OBS_VALUE:Observation Value']:
  check(rate['values'][c][y]==float(r['OBS_VALUE:Observation Value']),'BIS divergente');rate_rows+=1
check(rate_rows==sum(v is not None for values in rate['values'].values() for v in values.values()),'Juro sem linha bruta')
hourly=D['series']['hourly'];rawhours=list(csv.DictReader(io.StringIO((ROOT/'data'/hourly['rawFile']).read_text(encoding='utf-8-sig'))))
for row in rawhours:
 if row['REF_AREA'] in hourly['values']:
  expected=float(row['OBS_VALUE'])*10**int(row.get('UNIT_MULT') or 0) if row['OBS_VALUE'] else None
  check(close(hourly['values'][row['REF_AREA']][row['TIME_PERIOD']],expected),'Produtividade OCDE divergente')
# Todo valor exportado corresponde ao snapshot, inclusive nulos e flags.
csvrows=list(csv.DictReader((ROOT/'data/series.csv').open(encoding='utf-8-sig',newline='')))
check(len(csvrows)==sum(len(v) for s in D['series'].values() for v in s['values'].values()),'CSV incompleto')
for r in csvrows:
 s=D['series'][r['indicator']];v=s['values'][r['country']][r['period']]
 check(r['value']==('' if v is None else str(v)),'CSV alterado ou nulo virando zero')
 check(r['retrieved_at']==s['retrievedAt'] and r['source_url']==s['url'],'Proveniência CSV divergente')
for outcome,pools in A['outcomes'].items():
 for pool,models in pools.items():
  for mode,model in models.items():
   runs=[model,model['holdout']]+list(model['leaveOneOut'].values())+list(model['placebos'].values())
   for r in runs:
    w=r['weights'];target=r['target'];check(abs(sum(w.values())-1)<1e-9 and min(w.values())>=0,'Simplex violado')
    check(r['solver']['success'] and r['solver']['kktResidual']<=2e-5,'Solver não convergiu')
    check(r['solver']['objective']<=r['solver']['uniformObjective']+1e-9,'Objetivo pior que uniforme')
    check(abs(sum(p['v'] for p in r['predictorBalance'])-1)<1e-9,'V não normalizado')
    check(all(max(p['years'])<=r['trainEnd'] for p in r['predictorBalance']),'Vazamento temporal nos preditores')
    loss=0
    for p in r['predictorBalance']:
     raw_target=np.mean([D['series'][p['series']]['values'][target][str(y)] for y in p['years']])
     raw_synth=sum(z*np.mean([D['series'][p['series']]['values'][c][str(y)] for y in p['years']]) for c,z in w.items())
     check(close(float(raw_target),p['target']) and close(float(raw_synth),p['synthetic']),'Equilíbrio de preditores incorreto')
     if mode=='multivariate':
      raw_units=[np.mean([D['series'][p['series']]['values'][c][str(y)] for y in p['years']]) for c in [target]+list(w)]
      check(close(float(np.std(raw_units,ddof=1)),p['preSd']),'Escala usou unidades/anos errados')
     loss+=p['v']*((p['target']-p['synthetic'])/p['preSd'])**2
    check(close(loss,r['solver']['objective']),'Perda V/W divergente')
    values=D['series'][outcome]['values']
    for y,pred in r['predicted'].items():
     observed=all(values[c].get(y) is not None for c,z in w.items() if z>0)
     expected=sum(z*values[c][y] for c,z in w.items() if z>0) if observed else None
     check(close(pred,expected),'Predição com imputação ou peso errado')
     gap=values[target].get(y)-expected if values[target].get(y) is not None and expected is not None else None
     check(close(gap,r['gap'][y]),'Desvio errado')
    for years,name in [(list(range(2010,r['trainEnd']+1)),'preRmspe'),([2022,2023],'postRmspe')]+[([2018,2019,2020],'validationRmspe')]*(r['trainEnd']==2017):
     e=[r['gap'].get(str(y)) for y in years];value=math.sqrt(sum(x*x for x in e)/len(e)) if all(x is not None for x in e) else None
     check(close(value,r[name]),'Janela RMSPE divergente')
   check(set(model['leaveOneOut'])=={c for c,z in model['weights'].items() if z>.01},'Leave-one-out incompleto')
   check(set(model['placebos'])|set(model['excludedPlacebos'])==set(model['candidateDonors']),'Placebo omitido')
  if models['multivariate']['donors']==models['univariate']['donors']:
   check(models['univariate']['preRmspe']<=models['multivariate']['preRmspe']+1e-5,'Ótimo univariado inconsistente')
# Propriedades externas ao relatório: solução conhecida e invariância de unidade.
w,_=solve(np.eye(2),np.array([.25,.75]));check(np.max(np.abs(w-[.25,.75]))<1e-6,'Fixture convexa conhecida')
w,_=solve(np.eye(2),np.array([2.,0.]));check(np.max(np.abs(w-[1.,0.]))<1e-6,'Restrição na fronteira')
base=calculate(D,'inflation','TUR',PRINCIPAL)
altered=copy.deepcopy(D)
for c,values in altered['series']['income_ppp']['values'].items():
 for y,v in values.items():
  if v is not None:values[y]=v*1000
scaled=calculate(altered,'inflation','TUR',PRINCIPAL)
check(max(abs(base['weights'][c]-scaled['weights'][c]) for c in base['weights'])<1e-6,'Dependência da unidade monetária do preditor')
# Envenenar o futuro não pode mudar W, SD ou V do treino.
altered=copy.deepcopy(D)
for s in altered['series'].values():
 for c,values in s['values'].items():
  for y,v in values.items():
   if int(y[:4])>2020 and v is not None:values[y]=v+1e6
future=calculate(altered,'inflation','TUR',PRINCIPAL)
check(base['weights']==future['weights'] and base['predictorBalance']==future['predictorBalance'],'Vazamento do pós no treino')
holdout=calculate(D,'gdp','TUR',PRINCIPAL,end=2017)
altered=copy.deepcopy(D)
for s in altered['series'].values():
 for values in s['values'].values():
  for y,v in values.items():
   if int(y[:4])>=2018 and v is not None:values[y]=v+1e6
future=calculate(altered,'gdp','TUR',PRINCIPAL,end=2017)
check(holdout['weights']==future['weights'] and holdout['predictorBalance']==future['predictorBalance'],'Holdout consultou 2018–2020')
# País sem covariável permanece ausente do ajuste, sem receber média alheia.
check('NGA' in A['outcomes']['inflation']['extended']['multivariate']['excludedDonors'],'Nigéria sem preditores incluída')
check('NGA' in A['outcomes']['inflation']['extended']['univariate']['donors'],'Sensibilidade Nigéria perdida')
check(all(D['series']['gdp']['values'][c].get('2026') is None for c in D['countries']),'PIB anual 2026 preenchido')
check(all(v is None for y,v in hourly['values']['TUR'].items() if int(y)>=2022),'Horas turcas estendidas artificialmente')
for key in ['machinery_share','dwellings_share','other_buildings_share']:
 if key in D['series']:check(all(v is None for v in D['series'][key]['values']['TUR'].values()),'Componente turco inventado')
browser=json.loads((ROOT/'data/browser-validation.json').read_text(encoding='utf-8'))
for name,displayed in browser['eightModelCombinations'].items():
 outcome,pool,mode=name.split('-');r=A['outcomes'][outcome][pool][mode]
 actual=[r['preRmspe'],r['holdout']['validationRmspe'],r['ratio']]
 for shown,value in zip(displayed,actual):check(abs(float(shown.removesuffix('×').replace(',','.'))-value)<=.0051,'Diagnóstico visto no navegador diverge da análise final')
record=dict(checksPassed=checks,passed=True,snapshotSha256=A['metadata']['snapshotSha256'],analysisSha256=hashlib.sha256((ROOT/'data/analysis.json').read_bytes()).hexdigest(),validatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),properties=['Source checksums and rows','CSV and browser parity','W simplex and V weights','KKT and loss','Predictor balance','Temporal holdout without leakage','Unit invariance','Known convex solutions','Explicit missing-data exclusions'])
(ROOT/'data/validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
print(f'{checks} verificações passaram; dados, cálculo, propriedades e vazamento temporal conferidos.',flush=True)
