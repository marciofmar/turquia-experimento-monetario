'use strict';
const D=window.REPORT_DATA, $=id=>document.getElementById(id);
const colors={TUR:'#dc6537',BRA:'#16877c',POL:'#4267a6',HUN:'#8960a1',CZE:'#a18035',ROU:'#718c52',SRB:'#b75177',ZAF:'#425768',CHL:'#c28762',MEX:'#b24b48',MYS:'#55765a',THA:'#8a6780',COL:'#978827',IND:'#746139',NGA:'#6e719a',EGY:'#9d9a35',GHA:'#6b939a',OECD:'#233b50'};
const areaName=c=>D.countries[c]||D.extraAreas[c]||c;
const nf=new Intl.NumberFormat('pt-BR',{maximumFractionDigits:2}),fmt=v=>v==null||!Number.isFinite(Number(v))?'—':nf.format(Math.abs(Number(v))<0.005?0:v);
let chosen=['TUR','BRA','POL'], metric='inflation';
const allCharts=[];
function chart(id){const c=echarts.init($(id),null,{renderer:'svg'});allCharts.push(c);return c}
const main=chart('mainChart'),aChart=chart('structureA'),bChart=chart('structureB'),composition=chart('compositionChart'),synth=chart('synthChart'),hero=chart('heroChart');
function annualDate(y){return `${y}-07-01`}
function monthDate(m){const [y,n]=m.split('-').map(Number);return new Date(Date.UTC(y,n,0)).toISOString().slice(0,10)}
function dateOf(t){return t.length===4?annualDate(t):monthDate(t)}
function periodLabel(date){const s=new Date(date);return s.toLocaleDateString('pt-BR',{timeZone:'UTC',year:'numeric',month:metric==='rates'?'short':undefined})}
function range(){return [+$('from').value,+$('to').value]}
function shade(){return {silent:true,itemStyle:{color:'rgba(232,112,62,.10)'},data:[[{xAxis:'2021-09-01'},{xAxis:'2023-06-22'}]]}}
function options(series,min,max,unit,small=false){return {
 animation:false,color:chosen.map(c=>colors[c]),aria:{enabled:true,label:{enabled:true,description:`Gráfico com ${series.length} séries: ${series.map(s=>s.name).join(', ')}. Unidade: ${unit}. A faixa sombreada marca setembro de 2021 a junho de 2023. Consulte os dados e as notas metodológicas no relatório.`}},textStyle:{fontFamily:'Segoe UI, Arial, sans-serif'},
 tooltip:{trigger:'axis',confine:true,backgroundColor:'#fff',borderColor:'#c9d3d0',textStyle:{fontSize:11},valueFormatter:v=>fmt(v),axisPointer:{type:'line'}},
 legend:{type:'scroll',bottom:small?0:8,left:'center',textStyle:{fontSize:11,color:'#506570'},itemWidth:15,itemHeight:7},
 grid:{left:small?58:64,right:20,top:30,bottom:small?48:86},
 xAxis:{type:'time',min:`${min}-01-01`,max:`${max+1}-01-01`,splitNumber:small?4:8,axisLabel:{formatter:'{yyyy}',color:'#6c7b85',fontSize:10},axisLine:{lineStyle:{color:'#ccd7d2'}},axisTick:{show:false}},
 yAxis:{type:'value',scale:false,name:unit,nameTextStyle:{fontSize:10,color:'#78858d',align:'left',padding:[0,0,0,-45]},axisLabel:{fontSize:10,color:'#6c7b85',formatter:v=>nf.format(v)},splitLine:{lineStyle:{color:'#e8eeea',type:'dashed'}}},
 dataZoom:small?[]:[{type:'inside',filterMode:'none'},{type:'slider',bottom:37,height:15,borderColor:'transparent',fillerColor:'#e0e8e3',handleStyle:{color:'#728c83'},textStyle:{fontSize:9}}],series};}
function getSeries(key,c,transform='level'){
 const vals=D.series[key].values[c]||{},base=vals['2017'];
 return Object.entries(vals).sort(([a],[b])=>a.localeCompare(b)).map(([y,v])=>{
  let value=v;
  if(transform==='index')value=v==null||base==null||base===0?null:100*v/base;
  if(transform==='change'){const prev=vals[String(+y-1)];value=v==null||prev==null||prev===0?null:100*(v/prev-1)}
  return [y,value];
 });
}
const indexable=['fx','productivity','income'];
const notes={inflation:'Inflação média anual. Não compare diretamente com inflação acumulada em 12 meses até dezembro. A linha conecta observações anuais; não estima a trajetória mensal.',gdp:'Colunas mostram crescimento real anual, não o nível do PIB. O salto de 2021 inclui recuperação após a pandemia. Pontos anuais são posicionados no meio do ano; 2021 e 2023 misturam regimes monetários.',fx:'Moeda local por dólar, média anual oficial. Níveis de liras, reais e złotys não são comparáveis entre si; use o índice 2017 = 100 para comparar a variação proporcional. Câmbio oficial pode divergir do mercado em regimes com controles.',current:'Saldo em conta corrente em % do PIB: valores negativos indicam déficit. Melhora pode refletir mais exportações ou retração de importações e da demanda; não demonstra transformação produtiva.',rates:'Juros de fim de mês, não média anual. BIS a partir dos bancos centrais; instrumentos e regimes variam. A taxa de repo turca de 2017 não resume o custo efetivo de financiamento por outros instrumentos.',productivity:'PPC constante de 2021 por pessoa empregada. Não é produtividade por hora nem produtividade total dos fatores. Valores podem refletir composição e utilização do emprego.',investment:'Formação bruta de capital fixo / PIB. Não inclui toda a formação bruta de capital nem mede a qualidade ou o retorno do investimento.'};
function drawMain(){
 const [lo,hi]=range(),s=D.series[metric],t=$('transform').value;
 const unit=t==='index'?'2017 = 100':t==='change'?'% a.a.':s.unit;
 const series=chosen.map((c,i)=>({name:D.countries[c],type:metric==='gdp'?'bar':'line',data:getSeries(metric,c,t).filter(([y])=>+y.slice(0,4)>=lo&&+y.slice(0,4)<=hi).map(([y,v])=>[dateOf(y),v]),connectNulls:false,showSymbol:metric!=='rates',symbolSize:5,lineStyle:{width:c==='TUR'?3:2},itemStyle:{color:colors[c]},barMaxWidth:18,...(i===0?{markArea:shade()}:{}),step:metric==='rates'?'end':false}));
 if(series.length)series[0].markLine={silent:true,symbol:'none',lineStyle:{type:'dotted',color:'#ba856f',width:1},label:{position:'insideEndTop',fontSize:9,color:'#966145',formatter:p=>p.name},data:[{name:'Cortes · set. 2021',xAxis:'2021-09-01'},{name:'Reversão · jun. 2023',xAxis:'2023-06-22'}]};
 main.setOption(options(series,lo,hi,unit),true);
 $('chartTitle').textContent=s.label;$('chartUnit').textContent=unit+' · '+s.source;
 $('chartNote').textContent=(notes[metric]||'')+(t==='index'?' Base fixa 2017, mesmo quando o recorte começa depois.':t==='change'?' Variação calculada contra o ano anterior; não é diferença em pontos percentuais.':'');
 const missing=chosen.filter(c=>!getSeries(metric,c,t).some(([y,v])=>+y.slice(0,4)>=lo&&+y.slice(0,4)<=hi&&v!==null));
 $('availability').textContent=missing.length?'Sem observações no recorte: '+missing.map(c=>D.countries[c]).join(', ')+'.':'Linhas interrompidas e células “—” representam dados ausentes. 2026 não tem observação anual neste snapshot.';
 $('ratesTechnical').hidden=metric!=='rates';
 const periods=metric==='rates'?Array.from({length:(hi-lo+1)*12},(_,i)=>`${lo+Math.floor(i/12)}-${String(i%12+1).padStart(2,'0')}`):Array.from({length:hi-lo+1},(_,i)=>String(lo+i));
 const maps=Object.fromEntries(chosen.map(c=>[c,Object.fromEntries(getSeries(metric,c,t))]));
 $('dataTable').innerHTML=table(['Período',...chosen.map(c=>D.countries[c])],periods.map(y=>[y,...chosen.map(c=>fmt(maps[c][y]))]),`Valores de ${s.label} · ${unit}`);
 drawStructure();
}
function table(headers,rows,caption=''){return `<table>${caption?`<caption>${caption}</caption>`:''}<thead><tr>${headers.map(h=>`<th scope="col">${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map((c,i)=>i===0?`<th scope="row">${c}</th>`:`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`}
function drawStructure(){
 for(const [select,container,note,tableId] of [['structA',aChart,'structureNoteA','structureTableA'],['structB',bChart,'structureNoteB','structureTableB']]){
  const key=$(select).value,s=D.series[key],[lo,hi]=range(),areas=key==='hourly'?[...chosen,'OECD']:chosen;
  const ss=areas.map((c,i)=>({name:areaName(c),type:'line',connectNulls:false,showSymbol:true,symbolSize:4,lineStyle:{width:c==='TUR'?3:2,type:c==='OECD'?'dashed':'solid'},itemStyle:{color:colors[c]},data:getSeries(key,c).filter(([y])=>+y>=lo&&+y<=hi).map(([y,v])=>[annualDate(y),v]),...(i===0?{markArea:shade()}: {})}));
  container.setOption(options(ss,lo,hi,s.unit,true),true);
  $(note).textContent=`${s.unit}. Fonte: ${s.source}. Última observação no recorte: `+areas.map(c=>{const yrs=getSeries(key,c).filter(([y,v])=>+y>=lo&&+y<=hi&&v!=null);return areaName(c)+' '+(yrs.length?yrs.at(-1)[0]:'sem dado')}).join(' · ')+'.'+(key==='hourly'?' O agregado oficial OCDE é acrescentado como referência. A série turca termina em 2021; 2022–2025 ficam vazios. Não mede PTF.':key.endsWith('_share')?' Não há componente turco nesta fonte. Selecione pares como Polônia, México ou Hungria na Seção 02. Máquinas incluem sistemas de armas; não se calculou residual para preencher componentes ausentes.':'');
  const years=Array.from({length:hi-lo+1},(_,i)=>String(lo+i));
  $(tableId).innerHTML=table(['Ano',...areas.map(areaName)],years.map(y=>[y,...areas.map(c=>fmt(s.values[c]?.[y]))]),`${s.label} · ${s.unit}`);
 }
 drawComposition();
}
function drawComposition(){
 const c=$('structureCountry').value,[lo,hi]=range(),keys=['investment','manufacturing','exports'],palette=['#315667','#dc6537','#16877c'];
 const ss=keys.map((key,i)=>({name:D.series[key].label,type:'line',connectNulls:false,showSymbol:true,symbolSize:5,itemStyle:{color:palette[i]},data:getSeries(key,c).filter(([y])=>+y>=lo&&+y<=hi).map(([y,v])=>[annualDate(y),v]),...(i===0?{markArea:shade()}: {})}));
 composition.setOption(options(ss,lo,hi,'% do PIB'),true);
 $('compositionNote').textContent=areaName(c)+': razões nominais em % do PIB, com denominador comum. Mudanças de preços relativos e câmbio alteram as participações; não equivalem a volumes nem identificam retorno do investimento. Não há decomposição por ativo.';
 const years=Array.from({length:hi-lo+1},(_,i)=>String(lo+i));
 $('compositionTable').innerHTML=table(['Ano','FBCF / PIB','Manufatura / PIB','Exportações / PIB'],years.map(y=>[y,...keys.map(k=>fmt(D.series[k].values[c]?.[y]))]),areaName(c)+' · % do PIB');
}
function syncTransform(){const allowed=indexable.includes(metric);$('transform').disabled=!allowed;if(!allowed)$('transform').value='level'}
function renderCountries(){ $('countries').innerHTML=Object.entries(D.countries).map(([c,n])=>`<label class="chip"><input type="checkbox" value="${c}" ${chosen.includes(c)?'checked':''}><span style="color:${colors[c]}">●</span>${n}</label>`).join('');
 $('countries').querySelectorAll('input').forEach(input=>input.addEventListener('change',()=>{const selected=[...$('countries').querySelectorAll('input:checked')].map(x=>x.value);if(!selected.length){input.checked=true;return}chosen=selected;drawMain()})); }
function renderSynth(){
 const key=$('synthOutcome').value,pool=$('donorGroup').value,mode=$('synthMode').value,r=D.synthetic.outcomes[key][pool][mode],vals=D.series[key].values.TUR,gaps=$('synthView').value==='gaps';
 const ss=gaps?[{name:'Turquia − sintético',type:'line',connectNulls:false,itemStyle:{color:colors.TUR},data:Object.entries(r.gap).map(([y,v])=>[annualDate(y),v]),markArea:shade(),markLine:{silent:true,symbol:'none',data:[{yAxis:0}],lineStyle:{color:'#687a82',type:'dashed'}}}]:[{name:'Turquia',type:'line',connectNulls:false,itemStyle:{color:colors.TUR},lineStyle:{width:3},data:Object.entries(vals).filter(([y])=>+y<=2025).sort().map(([y,v])=>[annualDate(y),v]),markArea:shade()},{name:'Sintético',type:'line',connectNulls:false,itemStyle:{color:'#315667'},lineStyle:{type:'dashed',width:2},data:Object.entries(r.predicted).map(([y,v])=>[annualDate(y),v])}];
 synth.setOption(options(ss,2010,2025,gaps?'p.p.':'% a.a.'),true);
 const excluded=Object.entries(r.excludedDonors).map(([c,why])=>areaName(c)+': '+Object.keys(why).map(k=>D.series[k].label).join(', '));
 $('diagnostics').innerHTML=`<div class="diagnostic-grid"><div><b>${fmt(r.preRmspe)}</b>RMSPE pré · p.p.<br>2010–2020</div><div><b>${fmt(r.holdout.validationRmspe)}</b>RMSPE de validação · p.p.<br>2018–2020; treino até 2017</div><div><b>${fmt(r.ratio)}×</b>Razão RMSPE pós/pré<br>Pós = 2022–2023</div></div><p class="diagnostic-caption">${mode==='multivariate'?'V fixo: 50% para o histórico do desfecho e 50% para quatro covariáveis, padronizadas com dados do pré. O ajuste pode sacrificar proximidade da trajetória para equilibrar características produtivas.':'Somente o histórico anual do desfecho, com o mesmo objetivo univariado da edição anterior.'} ${r.donors.length} doadores elegíveis de ${r.candidateDonors.length} candidatos. ${excluded.length?'Exclusões por dados pré-tratamento incompletos: '+excluded.join('; ')+'.':'Preditores completos para todos os candidatos.'} Não houve seleção por resultado posterior.</p>`;
 const models=D.synthetic.outcomes[key][pool],candidates=D.synthetic.pools[pool];
 const weights=candidates.map(c=>[areaName(c),models.multivariate.weights[c]==null?'Excluído':fmt(models.multivariate.weights[c]*100)+'%',models.univariate.weights[c]==null?'Excluído':fmt(models.univariate.weights[c]*100)+'%']);
 const balance=r.predictorBalance.map(p=>[p.label+' · '+(p.years.length===1?p.years[0]:p.years[0]+'–'+p.years.at(-1)),fmt(p.target),fmt(p.synthetic),fmt(p.preSd),fmt(p.standardizedGap),fmt(p.v*100)+'%']);
 const sensitivity=Object.entries(r.leaveOneOut).map(([c,p])=>[areaName(c),fmt(p.preRmspe),fmt(p.gap['2022']),fmt(p.gap['2023'])]);
 const placebos=Object.entries(r.placebos).map(([c,p])=>[areaName(c),fmt(p.preRmspe),fmt(p.postRmspe),fmt(p.ratio)]);
 const gapsTable=Object.keys(r.predicted).map(y=>[y,fmt(vals[y]),fmt(r.predicted[y]),fmt(r.gap[y])]);
 $('robustness').innerHTML=`<p class="figure-note">W: pesos dos países. V: pesos dos preditores. São objetos diferentes. A validação refaz médias, escalas, V e W exclusivamente em 2010–2017; os valores de 2018–2020 não entram no treino. Cada resultado e cada pool têm seus próprios pesos. A mudança de elegibilidade entre modelos exige cautela na comparação.</p><div class="table-wrap">${table(['Doador','Multivariado','Univariado'],weights,'W · comparação dos dois ajustes no mesmo pool candidato')}</div><div class="table-wrap">${table(['Preditor / janela','Turquia','Sintético','Escala pré','Desvio / escala','V'],balance,'Equilíbrio dos preditores · modelo selecionado')}</div><p class="figure-note">Desvio Turquia − sintético: 2022 = ${fmt(r.gap['2022'])} p.p.; 2023 = ${fmt(r.gap['2023'])} p.p. São diferenças descritivas. KKT máximo: ${r.solver.kktResidual.toExponential(2)}; ${r.solver.iterations} iterações. V foi fixado antes do cálculo; não há busca de V pelo resultado pós-tratamento.</p><div class="table-wrap">${table(['Doador retirado','RMSPE pré','Desvio 2022','Desvio 2023'],sensitivity,'Leave-one-out · retiram-se pesos > 1%, com novo ajuste e novas escalas')}</div><div class="table-wrap">${table(['Alvo placebo','RMSPE pré','RMSPE pós','Razão pós/pré'],placebos,'Placebos espaciais · sem seleção por qualidade do ajuste, sem p-valor')}</div><p class="figure-note">Placebos não estimáveis: ${Object.keys(r.excludedPlacebos).map(areaName).join(', ')||'nenhum'}. Motivos completos em analysis.json. Nenhuma observação ausente foi substituída por zero.</p><details><summary>Valores anuais do contrafactual e lacunas</summary><div class="table-wrap">${table(['Ano','Turquia','Sintético','Desvio (p.p.)'],gapsTable,'Desfecho selecionado · % a.a.')}</div></details>`;
 const comp=D.synthetic.comparison[key],stages=[['Edição anterior · pool antigo',comp.beforeStored],['Dados novos · pool antigo · univariado',comp.beforePoolFreshData],['Pool principal · univariado',comp.principalUnivariate],['Pool principal · multivariado',comp.principalMultivariate]];
 $('beforeAfter').innerHTML=table(['Etapa','RMSPE pré (p.p.)','Pesos positivos (> 0,01%)'],stages.map(([label,p])=>[label,fmt(p.preRmspe),Object.entries(p.weights).filter(([,v])=>v>.0001).map(([c,v])=>areaName(c)+' '+fmt(v*100)+'%').join('; ')]),'Separar revisão dos dados, mudança do pool e mudança da especificação');
}
function renderSources(){
 const rows=Object.entries(D.series).map(([key,s])=>{
  const latest=Object.keys(s.values).map(c=>{const n=areaName(c);const dates=Object.entries(s.values[c]).filter(([,v])=>v!==null).map(([y])=>y).sort();return `${n}: ${dates.at(-1)||'sem série'}`}).join('; ');
  return [s.label,`<a href="${s.url}" target="_blank" rel="noopener">${s.code} ↗</a><br>${s.source}`,`${s.updated?'Base: '+s.updated+' · ':''}Consulta: ${s.retrievedAt.slice(0,10)}`,latest];
 });
 $('sources').innerHTML=table(['Indicador','Código / acesso direto','Atualização da base','Última observação não nula'],rows,'Inventário das séries e cobertura por país');
}
function renderKpis(){const entries=[['gdp','Crescimento real do PIB','%'],['inflation','Inflação média anual','%'],['rates','Juros · fim de mês','% a.a.']];$('kpis').innerHTML=entries.map(([key,label,unit])=>{const v=Object.entries(D.series[key].values.TUR).filter(([,v])=>v!==null).sort(([a],[b])=>a.localeCompare(b)).at(-1);return `<div class="kpi"><small>TURQUIA · ${v[0]}</small><strong>${fmt(v[1])}<small style="display:inline"> ${unit}</small></strong><span>${label}</span></div>`}).join('')}
for(let y=2017;y<=2026;y++){for(const id of ['from','to'])$(id).add(new Option(String(y),String(y)))}$('from').value='2017';$('to').value='2026';
const metricLabels={rates:'Juros',inflation:'Inflação',fx:'Câmbio',gdp:'PIB real',current:'Conta corrente',investment:'Investimento'};
$('metrics').innerHTML=Object.entries(metricLabels).map(([k,l])=>`<button class="metric-tab" data-key="${k}" aria-pressed="${metric===k}">${l}</button>`).join('');
$('metrics').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{metric=b.dataset.key;$('metrics').querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b));syncTransform();drawMain()}));
for(const id of ['from','to'])$(id).addEventListener('change',()=>{if(+$('from').value>+$('to').value){$(id==='from'?'to':'from').value=$(id).value}drawMain()});
$('structureCountry').innerHTML=Object.entries(D.countries).map(([c,n])=>`<option value="${c}">${n}</option>`).join('');$('structureCountry').addEventListener('change',drawComposition);
$('transform').addEventListener('change',drawMain);for(const id of ['structA','structB'])$(id).addEventListener('change',drawStructure);
for(const id of ['synthOutcome','donorGroup','synthMode','synthView'])$(id).addEventListener('change',renderSynth);
$('reset').addEventListener('click',()=>{chosen=['TUR','BRA','POL'];$('from').value='2017';$('to').value='2026';$('transform').value='level';renderCountries();drawMain()});
$('csv').addEventListener('click',()=>{const [lo,hi]=range(),s=D.series[metric],t=$('transform').value;const lines=['pais,indicador,periodo,valor,transformacao'];for(const c of chosen)for(const [y,v] of getSeries(metric,c,t))if(+y.slice(0,4)>=lo&&+y.slice(0,4)<=hi)lines.push([c,metric,y,v??'',t].join(','));const url=URL.createObjectURL(new Blob(['\ufeff'+lines.join('\r\n')],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`turquia-${metric}-${t}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
$('png').addEventListener('click',()=>{const link=document.createElement('a');link.href=main.getDataURL({type:'svg',backgroundColor:'#fff'});link.download=`turquia-${metric}.svg`;link.click()});
$('print').addEventListener('click',()=>window.print());
window.addEventListener('resize',()=>allCharts.forEach(c=>c.resize()));
const heroData=getSeries('inflation','TUR').filter(([y])=>+y>=2017&&+y<=2025);
hero.setOption({animation:false,grid:{left:10,right:20,top:25,bottom:28},xAxis:{type:'category',data:heroData.map(([y])=>y),axisLabel:{color:'#93a9b5',fontSize:10},axisLine:{lineStyle:{color:'#3d5360'}},axisTick:{show:false}},yAxis:{show:false},series:[{type:'line',data:heroData.map(([,v])=>v),symbolSize:6,itemStyle:{color:'#ff9a69'},lineStyle:{width:3,color:'#f39368'},areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(232,112,62,.25)'},{offset:1,color:'rgba(232,112,62,0)'}])},label:{show:true,color:'#eac7b8',fontSize:10,formatter:p=>p.dataIndex===heroData.length-1||p.dataIndex===5?fmt(p.value)+'%':''}}]});
const dDate=D.retrieved.split('-').reverse().join('/');$('retrievalDate').textContent='Fechamento da coleta: '+dDate;$('editionDate').textContent='edição revisada · '+dDate;
const tur=k=>D.series[k].values.TUR;
$('structuralReading').textContent=`No snapshot, a FBCF sobe de ${fmt(tur('investment')['2021'])}% do PIB em 2021 para ${fmt(tur('investment')['2025'])}% em 2025. A manufatura passa de ${fmt(tur('manufacturing')['2021'])}% em 2021 a ${fmt(tur('manufacturing')['2024'])}% em 2024; as exportações, de ${fmt(tur('exports')['2021'])}% a ${fmt(tur('exports')['2025'])}% em 2025. O PIB por empregado cresce ${fmt(100*(tur('productivity')['2025']/tur('productivity')['2021']-1))}% entre 2021 e 2025, sem medir separadamente horas e PTF.`;
renderCountries();renderKpis();renderSources();syncTransform();drawMain();renderSynth();
