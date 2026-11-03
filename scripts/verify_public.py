"""Verifica arquivos públicos; não substitui teste visual do navegador."""
import urllib.request,pathlib,json,hashlib,concurrent.futures,time,subprocess,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://marciofmar.github.io/turquia-experimento-monetario/'
FILES=['index.html','style.css','app.js','data/data.js','data/series.csv','data/analysis.json','data/snapshot.json','data/validation.json','data/browser-validation.json','data/baseline/analysis-v1.json','README.md','RELATORIO_TECNICO.md','scripts/analyze.py','scripts/fetch_data.py','scripts/config.py','scripts/validate.py','scripts/report.py','requirements.txt','data/raw-oecd-hourly.csv','data/raw-oecd-capital-attempt-0.csv','data/raw-wdi-income_ppp.json','data/raw-bis.zip']
def check(path):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(BASE+path+'?verification='+str(time.time_ns()),timeout=40) as res:remote=res.read();status=res.status
   local=(ROOT/path).read_bytes();is_raw=path.startswith('data/raw-') or path in ['data/series.csv','data/analysis.json','data/validation.json','data/snapshot.json'] or '/baseline/' in path
   matches=remote==local if is_raw else remote.replace(b'\r\n',b'\n')==local.replace(b'\r\n',b'\n')
   if matches:return dict(path=path,status=status,bytes=len(remote),sha256=hashlib.sha256(remote).hexdigest(),matchesLocal=True,comparison='bytes' if is_raw else 'text normalized LF')
  except (urllib.error.URLError,TimeoutError):
   if attempt==3:raise
  time.sleep(5)
 raise AssertionError('Arquivo público divergente: '+path)
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(check,FILES))
 validation=json.loads((ROOT/'data/validation.json').read_text(encoding='utf-8'))
 browser=json.loads((ROOT/'data/browser-validation.json').read_text(encoding='utf-8'))
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 record=dict(url=BASE,repository='https://github.com/marciofmar/turquia-experimento-monetario',verifiedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),testedSourceCommit=commit,snapshotSha256=validation['snapshotSha256'],analysisSha256=validation['analysisSha256'],dataChecksPassed=validation['checksPassed'],publicFiles=results,browserEvidence=browser,limits=['V fixo, sem identificação causal','RMSPE pré pior que edição anterior','Nigéria excluída do multivariado por FBCF e abertura ausentes','Componentes de FBCF da Turquia ausentes','PIB/hora turco termina em 2021'])
 (ROOT/'VALIDACAO.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 print(len(results),'arquivos públicos conferidos; respostas brutas e CSV idênticos em bytes; demais textos normalizados em LF.',flush=True)
if __name__=='__main__':main()
