import json,pathlib,hashlib,math
R=pathlib.Path(__file__).resolve().parents[1]
D=json.loads((R/'data/data.js').read_text(encoding='utf-8').removeprefix('window.REPORT_DATA=').removesuffix(';'))
checks=0
def check(condition,message):
 global checks
 assert condition,message
 checks+=1
for key,s in D['series'].items():
 for c,v in s['values'].items():
  check(all(x is None or isinstance(x,(int,float)) and math.isfinite(x) for x in v.values()),f'Valores inválidos {key}/{c}')
 if key!='rates':
  raw=(R/f'data/raw-wdi-{key}.json').read_bytes()
  check(hashlib.sha256(raw).hexdigest()==s['sha256'],f'Hash WDI {key}')
  rows=json.loads(raw)[1]
  for row in rows:check(s['values'][row['countryiso3code']][row['date']]==row['value'],f'Divergência {key}')
check(hashlib.sha256((R/'data/raw-bis.zip').read_bytes()).hexdigest()==D['bisSha256'],'Hash BIS')
for key,groups in D['synthetic'].items():
 values=D['series'][key]['values']
 for group,r in groups.items():
  runs=[('TUR',r,list(range(2010,2021))),('TUR',r['holdout'],list(range(2010,2018)))]+[('TUR',p,list(range(2010,2021))) for p in r['leaveOneOut'].values()]+[(c,p,list(range(2010,2021))) for c,p in r['placebos'].items()]
  for target,p,train in runs:
   w=p['weights'];check(abs(sum(w.values())-1)<1e-9 and min(w.values())>=0,'Simplex')
   for y,pred in p['predicted'].items():check(abs(pred-sum(z*values[c][y] for c,z in w.items()))<1e-8,'Predição ponderada')
   rms=math.sqrt(sum(p['gap'][str(y)]**2 for y in train)/len(train));check(abs(rms-p['preRmspe'])<1e-8,'RMSPE')
   objective=rms*rms*len(train)
   uniform=sum((values[target][str(y)]-sum(values[c][str(y)] for c in w)/len(w))**2 for y in train)
   check(objective<=uniform+1e-5,'Ajuste pior que pesos uniformes')
   # Condições KKT: gradientes iguais em pesos positivos, maiores nos zeros.
   grad={c:-2*sum(values[c][str(y)]*p['gap'][str(y)] for y in train) for c in w}
   lam=sum(w[c]*grad[c] for c in w)
   check(max(abs(grad[c]-lam) for c in w if w[c]>1e-5)<.03,'Otimização não convergiu nos pesos ativos')
   check(min(grad[c]-lam for c in w)>-.03,'Otimização não convergiu na fronteira')
for key in ['gdp','inflation','fx','current']:
 for c in ['TUR','BRA','POL']:check(D['series'][key]['values'][c]['2025'] is not None,f'2025 ausente: {key}/{c}')
check(not D['series']['rates']['values']['NGA'],'Ausência de juros Nigéria')
check(all(D['series']['gdp']['values'][c].get('2026') is None for c in D['countries']),'PIB2026 inventado')
print(f'{checks} verificações passaram: integridade das fontes, cobertura, pesos, previsões, RMSPE e convergência KKT.')
