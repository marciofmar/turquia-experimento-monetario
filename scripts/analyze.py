"""SCM multivariado com V fixo, diagnóstico completo e referência univariada."""
import json,pathlib,csv,hashlib,datetime,math
import numpy as np
import scipy
from scipy.optimize import minimize
from config import POOLS,LEGACY_POOLS,COVARIATES
ROOT=pathlib.Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def missing(series,country,years):return [str(y) for y in years if series.get(country,{}).get(str(y)) is None]
def eligibility(D,outcome,target,candidates,end,mode):
 years=list(range(2010,end+1));required=[outcome]+(COVARIATES if mode=='multivariate' else [])
 exclusions={}
 for c in [target]+candidates:
  reasons={k:missing(D['series'][k]['values'],c,years) for k in required}
  reasons={k:v for k,v in reasons.items() if v}
  if reasons:exclusions[c]=reasons
 if target in exclusions:raise ValueError(f'Alvo sem preditores completos: {target}: {exclusions[target]}')
 donors=[c for c in candidates if c not in exclusions]
 if len(donors)<2:raise ValueError('Menos de dois doadores elegíveis')
 return donors,exclusions

def definitions(outcome,end,mode):
 if mode=='univariate':return [dict(id=f'{outcome}_{y}',series=outcome,years=[y],v=1/(end-2009),block='outcome') for y in range(2010,end+1)]
 windows=[list(range(2010,2015)),list(range(2015,2018))]
 if end==2020:windows += [[2018],[2019],[2020]]
 assert end in [2017,2020]
 result=[dict(id=f'{outcome}_{min(w)}_{max(w)}',series=outcome,years=w,v=.5/len(windows),block='outcome') for w in windows]
 result += [dict(id=k+'_mean',series=k,years=list(range(2010,end+1)),v=.5/len(COVARIATES),block='covariate') for k in COVARIATES]
 return result

def matrices(D,outcome,target,donors,end,mode):
 defs=definitions(outcome,end,mode);units=[target]+donors
 raw=np.array([[np.mean([D['series'][p['series']]['values'][c][str(y)] for y in p['years']]) for c in units] for p in defs],dtype=float)
 if mode=='multivariate':
  center=raw.mean(axis=1);scale=raw.std(axis=1,ddof=1)
 else:
  # Uma escala comum preserva exatamente o objetivo univariado da versão anterior.
  center=np.zeros(len(defs));scale=np.full(len(defs),max(1,float(np.max(np.abs(raw)))))
 active=scale>1e-12
 if not np.all(active):
  for i in range(len(defs)):
   if not active[i]:defs[i]['v']=0
  total=sum(p['v'] for p in defs)
  for p in defs:p['v']/=total
  scale=np.where(active,scale,1)
 standardized=(raw-center[:,None])/scale[:,None]
 v=np.array([p['v'] for p in defs]);weighted=standardized*np.sqrt(v[:,None])
 return defs,raw,center,scale,v,weighted[:,1:],weighted[:,0]

def solve(A,b):
 n=A.shape[1];uniform=np.full(n,1/n)
 fun=lambda w:float(np.sum((A@w-b)**2))
 jac=lambda w:2*A.T@(A@w-b)
 result=minimize(fun,uniform,jac=jac,bounds=[(0,1)]*n,constraints=[{'type':'eq','fun':lambda w:float(w.sum()-1),'jac':lambda w:np.ones(n)}],method='SLSQP',options={'ftol':1e-12,'maxiter':2000})
 if not result.success:raise RuntimeError('SLSQP não convergiu: '+result.message)
 w=np.where(result.x<1e-12,0,result.x);w=w/w.sum()
 grad=jac(w);lam=float(w@grad);active=w>1e-7
 kkt=max(float(np.max(np.abs(grad[active]-lam))),max(0,float(np.max(lam-grad[~active]))) if np.any(~active) else 0)
 if kkt>2e-5:raise RuntimeError(f'Falha KKT: {kkt}')
 singular=np.linalg.svd(A,compute_uv=False);rank=int(np.linalg.matrix_rank(A))
 return w,dict(method='SLSQP',success=True,iterations=int(result.nit),ftol=1e-12,maxIterations=2000,kktResidual=kkt,objective=fun(w),uniformObjective=fun(uniform),weightedDesignRank=rank,nPredictors=A.shape[0],nDonors=n,conditionNumber=float(singular[0]/singular[-1]) if rank==min(A.shape) and singular[-1]>0 else None)

def calculate(D,outcome,target,candidates,end=2020,mode='multivariate'):
 donors,excluded=eligibility(D,outcome,target,candidates,end,mode)
 defs,raw,center,scale,v,A,b=matrices(D,outcome,target,donors,end,mode)
 w,solver=solve(A,b);weights={c:float(z) for c,z in zip(donors,w)}
 vals=D['series'][outcome]['values'];predicted={};gap={};missing_predictions={}
 for y in range(2010,2026):
  key=str(y);absent=[c for c in donors if weights[c]>0 and vals[c].get(key) is None]
  predicted[key]=sum(weights[c]*vals[c][key] for c in donors if weights[c]>0) if not absent else None
  gap[key]=vals[target].get(key)-predicted[key] if vals[target].get(key) is not None and predicted[key] is not None else None
  if absent:missing_predictions[key]=absent
 def rmse(years):
  # Uma janela incompleta não é silenciosamente reduzida.
  errors=[gap.get(str(y)) for y in years]
  return math.sqrt(sum(x*x for x in errors)/len(errors)) if all(x is not None for x in errors) else None
 pre=rmse(list(range(2010,end+1)));post=rmse([2022,2023])
 balance=[]
 for i,p in enumerate(defs):
  synthetic=float(raw[i,1:]@w);diff=float((raw[i,0]-synthetic)/scale[i])
  balance.append(dict(**p,label=D['series'][p['series']]['label'],target=float(raw[i,0]),synthetic=synthetic,preMean=float(center[i]),preSd=float(scale[i]),standardizedGap=diff,lossContribution=float(v[i]*diff**2)))
 return dict(target=target,mode=mode,trainStart=2010,trainEnd=end,weights=weights,candidateDonors=candidates,donors=donors,excludedDonors=excluded,predicted=predicted,gap=gap,missingPredictions=missing_predictions,preRmspe=pre,validationRmspe=rmse([2018,2019,2020]) if end==2017 else None,postRmspe=post,ratio=post/pre if post is not None and pre is not None and pre>1e-8 else None,predictorBalance=balance,solver=solver)

def main():
 D=json.loads((ROOT/'data/snapshot.json').read_text(encoding='utf-8'))
 outcomes={}
 for key in ['inflation','gdp']:
  outcomes[key]={}
  for pool,candidates in POOLS.items():
   outcomes[key][pool]={}
   for mode in ['multivariate','univariate']:
    r=calculate(D,key,'TUR',candidates,mode=mode)
    r['holdout']=calculate(D,key,'TUR',candidates,end=2017,mode=mode)
    r['leaveOneOut']={c:calculate(D,key,'TUR',[d for d in candidates if d!=c],mode=mode) for c,z in r['weights'].items() if z>.01}
    r['placebos']={};r['excludedPlacebos']={}
    for c in candidates:
     try:r['placebos'][c]=calculate(D,key,c,[d for d in candidates if d!=c],mode=mode)
     except ValueError as e:r['excludedPlacebos'][c]=str(e)
    outcomes[key][pool][mode]=r
    print(key,pool,mode,'RMSPE',round(r['preRmspe'],4),'validação',round(r['holdout']['validationRmspe'],4),'doadores',len(r['donors']),flush=True)
 baseline=json.loads((ROOT/'data/baseline/analysis-v1.json').read_text(encoding='utf-8'))
 comparison={}
 for key in outcomes:
  old_fresh=calculate(D,key,'TUR',LEGACY_POOLS['all'],mode='univariate')
  uni=outcomes[key]['principal']['univariate'];multi=outcomes[key]['principal']['multivariate']
  comparison[key]=dict(beforeStored={k:baseline[key]['all'][k] for k in ['preRmspe','weights','gap']},beforePoolFreshData=old_fresh,principalUnivariate={k:uni[k] for k in ['preRmspe','weights','gap']},principalMultivariate={k:multi[k] for k in ['preRmspe','weights','gap']})
 metadata=dict(schemaVersion=2,dataRetrievedAt=D['retrievedAt'],snapshotSha256=digest(ROOT/'data/snapshot.json'),codeSha256={name:digest(ROOT/'scripts'/name) for name in ['config.py','analyze.py','fetch_data.py']},baselineCommit='d88ee5e',baselineAnalysisSha256=digest(ROOT/'data/baseline/analysis-v1.json'),numpy=np.__version__,scipy=scipy.__version__,trainingYears=[2010,2020],holdoutTrainingYears=[2010,2017],holdoutEvaluationYears=[2018,2020],postYears=[2022,2023],covariates=COVARIATES,vRule='Fixo ex ante: histórico do desfecho 0.5, covariáveis 0.5. Divisão uniforme dentro de cada bloco. Não estimado pelo pós nem pelo holdout.',standardization='Multivariado: média e desvio-padrão amostral entre alvo e doadores elegíveis, por preditor agregado exclusivamente no pré. Univariado: escala numérica comum, sem mudar o objetivo histórico.',missingPolicy='Exigir todas as observações pré-tratamento dos preditores; excluir doador incompleto com motivo. Não selecionar doadores pela disponibilidade pós. Previsão pós ausente se faltar desfecho de doador com peso positivo.')
 result=dict(schemaVersion=2,metadata=metadata,pools=POOLS,outcomes=outcomes,comparison=comparison)
 (ROOT/'data/analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
 D['synthetic']=result
 (ROOT/'data/data.js').write_text('window.REPORT_DATA='+json.dumps(D,ensure_ascii=False,allow_nan=False)+';',encoding='utf-8')
 with (ROOT/'data/series.csv').open('w',newline='',encoding='utf-8-sig') as f:
  writer=csv.writer(f);writer.writerow(['country','indicator','period','value','unit','source_url','retrieved_at','observation_status'])
  for key,s in D['series'].items():
   for c,values in s['values'].items():
    for year,value in sorted(values.items()):writer.writerow([c,key,year,'' if value is None else value,s['unit'],s['url'],s['retrievedAt'],s.get('observationStatus',{}).get(c,{}).get(year,'')])
 print('Análise e séries regeneradas a partir do snapshot completo.',flush=True)
if __name__=='__main__':main()
