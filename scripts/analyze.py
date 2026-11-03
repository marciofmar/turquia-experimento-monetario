"""Controle sintético exploratório univariado, simplex, sem imputação."""
import json,math,pathlib,csv
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/snapshot.json').read_text(encoding='utf-8'))
ROWS=json.loads((ROOT/'data/bis-rows.json').read_text(encoding='utf-8'))
ISO={'TR':'TUR','BR':'BRA','PL':'POL','HU':'HUN','CZ':'CZE','RO':'ROU','RS':'SRB','ZA':'ZAF','CL':'CHL','NG':'NGA','EG':'EGY','GH':'GHA'}
rates={c:{} for c in D['countries']}; metadata={}
for r in ROWS:
 c=ISO.get(r['REF_AREA:Reference area'].split(':')[0]); date=r['TIME_PERIOD:Time period or range']
 if c and r['FREQ:Frequency'].startswith('M:') and '2010-01'<=date<='2026-11' and r['OBS_VALUE:Observation Value']:
  rates[c][date]=float(r['OBS_VALUE:Observation Value']); metadata[c]={'compilation':r['COMPILATION:Compilation'],'source':r['SOURCE_REF:Publication Source'],'breaks':r['SUPP_INFO_BREAKS:Supplemental information and breaks']}
D['series']['rates']=dict(label='Juros de política monetária',unit='% a.a. · fim do mês',source='BIS · bancos centrais nacionais',code='WS_CBPOL · M',url=D['bisSource'],values=rates,metadata=metadata)
def simplex(v):
 u=sorted(v,reverse=True); s=0; theta=0
 for j,x in enumerate(u,1):
  s+=x; t=(s-1)/j
  if x>t: theta=t
 return [max(x-theta,0) for x in v]
def fit(values,target,donors,years):
 scale=max(1,max(abs(values[c][str(y)]) for c in [target]+donors for y in years))
 A=[[values[c][str(y)]/scale for c in donors] for y in years]; b=[values[target][str(y)]/scale for y in years]
 w=[1/len(donors)]*len(donors); step=1/(2*sum(x*x for row in A for x in row))
 for it in range(25000):
  residual=[sum(x*z for x,z in zip(row,w))-t for row,t in zip(A,b)]
  nw=simplex([z-step*2*sum(row[j]*e for row,e in zip(A,residual)) for j,z in enumerate(w)])
  if max(abs(x-y) for x,y in zip(w,nw))<1e-10:break
  w=nw
 return w
def calc(values,target,donors,train):
 w=fit(values,target,donors,train)
 predicted={str(y):sum(z*values[c][str(y)] for c,z in zip(donors,w)) for y in range(2010,2026) if all(values[c].get(str(y)) is not None for c in donors)}
 gap={y:values[target][y]-v for y,v in predicted.items() if values[target].get(y) is not None}
 def rmse(yrs):
  v=[gap[str(y)]**2 for y in yrs if str(y) in gap];return math.sqrt(sum(v)/len(v)) if v else None
 return dict(weights={c:z for c,z in zip(donors,w)},predicted=predicted,gap=gap,preRmspe=rmse(train),validationRmspe=rmse(range(2018,2021)),postRmspe=rmse([2022,2023]),iterationsLimit=25000)
groups={'all':[c for c in D['countries'] if c!='TUR'],'europe':['POL','HUN','CZE','ROU','SRB'],'emerging':['BRA','CHL','ZAF','NGA','EGY','GHA']}
out={}
for key in ['inflation','gdp']:
 values=D['series'][key]['values']; out[key]={}
 for group,donors in groups.items():
  donors=[c for c in donors if all(values[c].get(str(y)) is not None for y in range(2010,2024))]
  result=calc(values,'TUR',donors,list(range(2010,2021)))
  result['holdout']=calc(values,'TUR',donors,list(range(2010,2018)))
  result['leaveOneOut']={c:calc(values,'TUR',[d for d in donors if d!=c],list(range(2010,2021))) for c,w in result['weights'].items() if w>0.01}
  placebos={}
  for target in donors:
   p=calc(values,target,[c for c in donors if c!=target],list(range(2010,2021)))
   p['ratio']=p['postRmspe']/p['preRmspe'] if p['preRmspe']>1e-8 else None
   placebos[target]=p
  result['placebos']=placebos; result['donors']=donors
  result['ratio']=result['postRmspe']/result['preRmspe'] if result['preRmspe']>1e-8 else None
  out[key][group]=result
D['synthetic']=out
(ROOT/'data/analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/data.js').write_text('window.REPORT_DATA='+json.dumps(D,ensure_ascii=False)+';',encoding='utf-8')
with (ROOT/'data/series.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.writer(f);writer.writerow(['country','indicator','period','value','unit','source_url'])
 for key,s in D['series'].items():
  for c,values in s['values'].items():
   for y,v in sorted(values.items()):writer.writerow([c,key,y,'' if v is None else v,s['unit'],s['url']])
print('BIS latest', {c:max(v,default=None) for c,v in rates.items()})
print('Main synthetic', {k:{g:{n:r[n] for n in ['preRmspe','validationRmspe','ratio','weights']} for g,r in v.items()} for k,v in out.items()})
