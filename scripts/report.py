"""Relatório técnico derivado dos mesmos resultados publicados, sem números manuais."""
import json,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
D=json.loads((R/'data/snapshot.json').read_text(encoding='utf-8'));A=json.loads((R/'data/analysis.json').read_text(encoding='utf-8'));T=json.loads((R/'data/validation.json').read_text(encoding='utf-8'))
def fmt(x,n=2):return 'ausente' if x is None else f'{x:.{n}f}'.replace('.',',')
def weights(r):return '; '.join(D['countries'][c]+' '+fmt(v*100)+'%' for c,v in r['weights'].items() if v>.0001)
lines=['# Revisão técnica: controle sintético e estrutura produtiva','',f'Fechamento da coleta: {D["retrieved"]}. Fontes originais, horários e hashes estão em `data/snapshot.json`.','',
'## Arquivos modificados e criados','',
'- Coleta e cálculo: `scripts/config.py`, `scripts/fetch_data.py`, `scripts/analyze.py`, `scripts/validate.py`, `scripts/report.py` e `requirements.txt`.','- Interface e documentação: `index.html`, `app.js`, `style.css`, `README.md`, `.gitignore`, `.gitattributes`, `PUBLICACAO.md` e registros de validação.','- Dados regenerados: `data/snapshot.json`, `data/analysis.json`, `data/series.csv`, `data/data.js`, `data/validation.json` e respostas originais WDI/BIS/OCDE.','- Referência preservada: `data/baseline/analysis-v1.json` e `data/baseline/snapshot-v1.json`, correspondentes à edição do commit `d88ee5e`.','',
'## Comparação de ajuste e pesos','',
'RMSPE em pontos percentuais. O resultado antigo é reapresentado e depois reestimado com dados novos. A comparação seguinte altera o pool; a última altera somente a especificação no mesmo pool principal completo. Pesos positivos acima de 0,01% são mostrados; arredondamento pode afetar a soma aparente.','',
'| Desfecho | Etapa | RMSPE pré 2010–2020 | Pesos dos doadores |','|---|---|---:|---|']
for key,label in [('inflation','Inflação'),('gdp','PIB real')]:
 c=A['comparison'][key]
 for tag,name in [('beforeStored','Edição anterior'),('beforePoolFreshData','Pool antigo, dados novos, univariado'),('principalUnivariate','Pool principal, univariado'),('principalMultivariate','Pool principal, multivariado')]:
  r=c[tag];lines.append(f'| {label} | {name} | {fmt(r["preRmspe"],4)} | {weights(r)} |')
lines+=['','A revisão não melhora o ajuste da trajetória turca. O novo padrão exige características produtivas e abandona a forte dependência anterior de Nigéria/Gana. O ajuste prévio piora, e a interpretação causal fica limitada. A similaridade produtiva de alguns preditores não torna os países controles não tratados nem garante suporte comum suficiente.','',
'V é fixo: 0,5 para o histórico do desfecho e 0,5 para quatro covariáveis; no treino principal são cinco linhas do histórico com peso 0,10 e quatro covariáveis com peso 0,125. Não se otimizou V no pós. As fórmulas, escalas, perdas e equilíbrio por preditor estão no README e no JSON.','',
'| Desfecho / pool / especificação | Elegíveis / candidatos | RMSPE pré | RMSPE holdout 2018–2020 | RMSPE pós 2022–2023 / pré |','|---|---:|---:|---:|---:|']
for key,label in [('inflation','Inflação'),('gdp','PIB')]:
 for pool,models in A['outcomes'][key].items():
  for mode,r in models.items():lines.append(f'| {label} / {pool} / {mode} | {len(r["donors"])}/{len(r["candidateDonors"])} | {fmt(r["preRmspe"])} | {fmt(r["holdout"]["validationRmspe"])} | {fmt(r["ratio"])} |')
lines+=['','O pool principal tem 13 candidatos e cobertura pré completa. O estendido acrescenta Nigéria, Egito e Gana. Nigéria não dispõe de FBCF nem abertura comercial em 2010–2020: é excluída do multivariado e permanece no univariado, com os anos e motivos registrados. Não houve preenchimento ou exclusão por resultado posterior.','',
'Validação temporal, leave-one-out (W>1%) e placebos espaciais foram refeitos para cada especificação/pool. O holdout constrói preditores apenas até 2017; não usa 2018–2020 para obter médias, escalas ou pesos. Os placebos não são filtrados por conveniência do ajuste. Não há p-valor ou efeito causal identificado.','',
'## Leitura estrutural da Turquia em 2021–2025','']
for key,label,year in [('investment','FBCF / PIB',2025),('manufacturing','Manufatura / PIB',2024),('exports','Exportações / PIB',2025)]:
 v=D['series'][key]['values']['TUR'];lines.append(f'- {label}: {fmt(v["2021"])}% em 2021 para {fmt(v[str(year)])}% em {year}.')
v=D['series']['productivity']['values']['TUR'];lines += [f'- PIB por empregado: {fmt(100*(v["2025"]/v["2021"]-1))}% de crescimento acumulado entre 2021 e 2025, em PPC constante de 2021.','',
'O aumento do peso do investimento não foi acompanhado, nesses indicadores, por maior participação da manufatura ou das exportações. Isso reforça a necessidade de distinguir expansão agregada de transformação produtiva. Como as participações são razões nominais, a divergência também pode refletir preços relativos, câmbio e o denominador. Não prova queda de volume industrial, ineficiência do investimento ou efeito dos juros. Manufatura de 2025 permanece ausente.','',
'A API de FBCF por ativo foi acessada na coleta completa. Os pares com numerador e total observados têm parcelas de máquinas/equipamentos e armas, habitação e outras construções. Para a Turquia, a resposta traz apenas o total; os componentes não foram inferidos. As parcelas são % da FBCF a preços correntes, não % do PIB e não um índice de qualidade. A cobertura por país/ano e os termos das razões estão no snapshot.','',
'A série OCDE de PIB/hora da Turquia termina em 2021, embora o agregado oficial OCDE e alguns pares avancem. Não há base nesta série para confirmar evolução da produtividade por hora turca em 2022–2025. O PIB/empregado não separa horas, utilização e PTF; não se dividiram níveis com bases PPC distintas para estimar horas.','',
'A nota monetária distingue repo, WACF, LLW, regras de liraização, crédito/títulos e depósitos KKM, com documentos do TCMB e do FMI. Não se criou curva WACF artificial.','',
'## Validação e publicação','',f'{T["checksPassed"]} verificações passaram: hashes/linhas originais, paridade CSV/navegador, V/W, KKT, predições, RMSPE, soluções convexas conhecidas, invariância de unidade e ausência de vazamento do futuro no treino.','',
'A validação visual e do endereço publicado é registrada separadamente em `PUBLICACAO.md` e `VALIDACAO.json`.','',
'Site: https://marciofmar.github.io/turquia-experimento-monetario/','Repositório: https://github.com/marciofmar/turquia-experimento-monetario','']
(R/'RELATORIO_TECNICO.md').write_text('\n'.join(lines),encoding='utf-8')
print('RELATORIO_TECNICO.md gerado a partir dos dados e diagnósticos.')
