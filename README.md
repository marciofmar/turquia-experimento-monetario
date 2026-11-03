# Turquia: crescimento e estrutura

Relatório estático em português, com 17 países, dados WDI/BIS/OCDE e controles sintéticos exploratórios. O modelo padrão é multivariado. A referência univariada e a edição anterior permanecem auditáveis. Site: https://marciofmar.github.io/turquia-experimento-monetario/.

## Reprodução do início ao fim

Python 3.14 foi utilizado nesta edição. As versões testadas estão em `requirements.txt`. Os scripts de extração usam a biblioteca padrão; a análise usa NumPy e SciPy.

```sh
python -m venv .venv
# Windows:
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python scripts/fetch_data.py
.venv\Scripts\python scripts/analyze.py
.venv\Scripts\python scripts/validate.py
.venv\Scripts\python scripts/report.py
node --check app.js
# Servir a pasta atual, ou abrir index.html diretamente:
python -m http.server 8787
```

Em Linux/macOS, substitua `.venv\Scripts\python` por `.venv/bin/python`. Não há build de front-end. O ECharts 5.6.0 e os dados do navegador são locais. Conexão é necessária para uma nova coleta e para abrir links de fontes, não para desenhar gráficos.

1. `scripts/config.py` fixa países, códigos e pools antes de estimar.
2. `fetch_data.py` baixa novamente WDI, BIS e OCDE. Mantém respostas em memória até terminar a coleta, preservando a edição anterior se uma fonte falhar. Guarda bytes originais, URLs, SHA-256, horário de consulta e flags. Ao concluir, substitui os arquivos brutos e grava atomicamente `snapshot.json`. Recusas HTTP são registradas; uma falha total de acesso não vira uma série econômica vazia nem uma nova edição incompleta.
3. `analyze.py` lê esse snapshot completo, estima os dois modelos nos dois pools e todos os diagnósticos. Gera `analysis.json`, `data.js` e `series.csv` a partir dos mesmos valores.
4. `validate.py` confere proveniência, dados, contas, equilíbrio, convergência, ausência de vazamento temporal e propriedades do estimador. Gera `data/validation.json` sem alterar os dados.
5. `report.py` gera `RELATORIO_TECNICO.md` a partir dos resultados e da validação.

Uma nova consulta pode revisar valores históricos, cobertura e data de atualização. A data não é constante no código: o snapshot registra início e fechamento da coleta, além dos horários por fonte. Não há atualização agendada. Os períodos de análise continuam fixos até 2025 para resultados anuais e até o mês corrente para a coleta de juros; isso não cria dados futuros.

## Matriz de preditores, V e W

Para cada desfecho (inflação média ou crescimento real do PIB), há J doadores e um alvo. A matriz bruta `R` tem uma coluna para o alvo e uma para cada doador. No treino principal 2010–2020, suas nove linhas são:

| Bloco | Preditor | Janela | Peso diagonal de V |
|---|---|---|---:|
| Desfecho | Média do desfecho | 2010–2014 | 0,10 |
| Desfecho | Média do desfecho | 2015–2017 | 0,10 |
| Desfecho | Valor do desfecho | 2018 | 0,10 |
| Desfecho | Valor do desfecho | 2019 | 0,10 |
| Desfecho | Valor do desfecho | 2020 | 0,10 |
| Estrutura | PIB per capita PPC constante (NY.GDP.PCAP.PP.KD) | média 2010–2020 | 0,125 |
| Estrutura | FBCF/PIB (NE.GDI.FTOT.ZS) | média 2010–2020 | 0,125 |
| Estrutura | Abertura comercial/PIB (NE.TRD.GNFS.ZS) | média 2010–2020 | 0,125 |
| Estrutura | Manufatura/PIB (NV.IND.MANF.ZS) | média 2010–2020 | 0,125 |

Em cada linha k, sejam `mu_k` e `s_k` a média e o desvio-padrão amostral **entre alvo e doadores elegíveis** dos preditores pré-tratamento agregados. A padronização é:

```text
mu_k = (1/(J+1)) × sum_i R_ki
s_k² = (1/J) × sum_i (R_ki - mu_k)²
X_ki = (R_ki - mu_k) / s_k
V = diag(v_1, ..., v_K), v_k >= 0, sum(v_k) = 1

W* = argmin_W (X_1 - X_0 W)' V (X_1 - X_0 W)
sujeito a w_j >= 0 e sum_j w_j = 1

Y_sintético,t = sum_j w_j Y_jt
desvio_t = Y_Turquia,t - Y_sintético,t
RMSPE(T) = sqrt((1/|T|) × sum_t em T desvio_t²)
```

`X_1` é a coluna do alvo e `X_0`, a matriz dos doadores. O desvio-padrão é transversal de preditores construídos no pré, não volatilidade temporal de séries mensais. Centro e escala são refeitos em cada ajuste, inclusive leave-one-out e placebo. Se uma linha tiver desvio-padrão zero, seu peso é retirado e V renormalizado, com registro no equilíbrio; essa regra não foi necessária nos modelos principais desta edição.

**V é fixo, não estimado:** 50% ao histórico do desfecho e 50% às características estruturais, dividido uniformemente dentro dos blocos. Essa escolha evita que o número de linhas de um bloco determine seu peso e não usa o resultado posterior. Ela não reproduz a busca aninhada de V de algumas implementações de Synth. É uma escolha normativa, não uma estimativa de relevância econômica; outros V podem alterar pesos e conclusões. W contém os pesos dos países, enquanto V contém os pesos dos preditores. A interface mostra ambos e o desvio padronizado por preditor.

O objetivo é convexo em W com V fixo. SLSQP, gradiente analítico, inicialização uniforme, `ftol=1e-12`, `maxiter=2000`. A solução precisa satisfazer as restrições e condições KKT com resíduo máximo de 2e-5 na escala do objetivo. Pesos inferiores a 1e-12 são tratados como zero numérico e o vetor é renormalizado; não se trata de imputação de dados. Perda, condição/rank da matriz ponderada, iterações e resíduo KKT ficam no JSON. Com muitos países e poucos preditores pode haver W não único; a inicialização fixa permite reproduzir a solução apresentada. Não se deve interpretar um peso individual como importância causal de um país.

### Univariado auditável

Usa uma linha para cada valor anual do desfecho em 2010–2020, V proporcional à identidade e uma escala numérica comum a todas as linhas/países. Minimiza a mesma soma de quadrados anual da edição anterior. Essa especificação não adiciona características estruturais. Seu RMSPE pré deve ser menor ou igual ao do multivariado com o mesmo conjunto elegível: o multivariado otimiza outro critério e pode sacrificar o ajuste da trajetória.

### Donor pools e integridade

Principal: México, Polônia, Brasil, África do Sul, Malásia, Tailândia, Romênia, Hungria, Colômbia, Chile, Índia, Tchéquia e Sérvia (13 candidatos). São comparadores produtivos e comerciais, sem alegação de identidade estrutural ou classificação oficial uniforme de emergentes. Commodities, renda, instituições e inserção europeia ainda diferem; os preditores tornam parte dessas diferenças visível, sem removê-las por completo.

Estendido: os mesmos 13 mais Nigéria, Egito e Gana, exclusivamente para sensibilidade. **Nigéria não possui FBCF nem abertura comercial na WDI em 2010–2020.** Fica fora do multivariado (15 elegíveis) e dentro do univariado (16). Não é substituída por um país inventado, não recebe média de outro país e não se remove uma covariável de todo o modelo para mantê-la. Sua exclusão e os anos ausentes são explícitos em `excludedDonors` e na interface. Comparar esses dois ajustes estendidos altera também a elegibilidade.

Uma observação pré-tratamento ausente em qualquer preditor necessário exclui o doador daquele ajuste. Médias exigem todos os anos da janela; não se usam médias parciais. **Nenhuma seleção de doador depende de valores após o treino.** Se faltar o desfecho posterior de um doador com peso positivo, a previsão desse ano fica nula; uma janela de RMSPE incompleta também fica nula, em vez de mudar silenciosamente os anos avaliados.

### Diagnósticos refeitos

- Treino principal 2010–2020; 2021 não entra no treino nem na razão pós/pré. Pós: 2022 e 2023. Em 2023 há terremotos e reversão monetária; 2024–2025 são acompanhamento de outro regime.
- Validação temporal: novo treino 2010–2017 e teste 2018–2020. O multivariado usa apenas duas médias do desfecho (2010–2014 e 2015–2017), cada uma com V=0,25; as quatro covariáveis têm médias até 2017 e V=0,125. Médias, escalas e elegibilidade não consultam 2018 em diante. É validação fora da amostra, não uma intervenção real em 2018.
- Leave-one-out: retirar cada país com W>1%, refazer elegibilidade, escalas e W na mesma especificação.
- Placebos espaciais: cada candidato elegível vira alvo; os outros candidatos são doadores, sem Turquia. Mesma especificação e mesmas janelas. Casos não estimáveis são registrados; ajustes ruins não são descartados para favorecer a Turquia. Razão RMSPE pós/pré: 2022–2023 / 2010–2020. Não há p-valor, atribuição aleatória ou intervalo causal.

`data/baseline/analysis-v1.json` e `snapshot-v1.json` preservam a edição anterior (commit `d88ee5e`). A comparação distingue: resultado antigo armazenado; reestimação do pool antigo com dados novos; novo pool univariado; novo pool multivariado. Isso separa revisão de dados, seleção do pool e especificação. Os pesos entre duas especificações só isolam a mudança metodológica quando a elegibilidade também é igual.

## Estrutura produtiva e limites de cobertura

WDI: FBCF total, manufatura/PIB e exportações de bens e serviços/PIB aparecem juntos para o mesmo país. São razões a preços correntes; mudanças de câmbio, preços relativos e denominador não equivalem a variações de volume. Não identificam retorno do capital, desindustrialização em termos reais ou causalidade monetária.

OCDE `DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_GFCF_ASSET,1.0`: setor S1, contraparte S1, P51G, preços correntes V, moeda nacional XDC, transformação N, atividade total e tabela T0102. Os ativos são N11MG (máquinas/equipamentos **e sistemas de armas**), N111G (habitação) e N112G (outras edificações/estruturas). Calcula-se `100 × componente / N11G`, somente com numerador e denominador observados do mesmo país, ano, moeda e escala. Valores originais e flags dos dois termos ficam em `components`; não se calcula residual para preencher outro ativo. Os componentes mostrados não esgotam a FBCF.

A resposta consultada fornece componentes para pares, mas **somente o total N11G para a Turquia**. As parcelas turcas ficam vazias. A cobertura efetiva e as tentativas de consulta ficam no snapshot. Algumas consultas iniciais foram recusadas, mas a coleta completa acessou o conjunto; a conclusão de falta de componentes se baseia na resposta obtida, não no erro HTTP. A fonte não foi substituída por uma decomposição inferida do PIB.

OCDE `DSD_PDB@DF_PDB,2.0`: PIB por hora, GDPHRS, LR, USD_PPP_H, N, atividade total, base 2020 verificada. A série turca termina em 2021; 2022–2025 são nulos. O agregado oficial OCDE é acrescentado como referência, sem calcular uma média simples dos pares. O PIB por trabalhador WDI usa PPC de 2021. Não dividimos níveis com bases/fontes diferentes para inferir horas. PIB/hora continua dependendo de capital, composição e utilização; não é PTF. Não se construiu série de PTF sem uma fonte reprodutível confirmada.

## Juros oficiais, WACF e mecanismos de transmissão

O BIS compila taxas de política de fim de mês a partir dos bancos centrais, com mudanças de instrumentos registradas. Para a Turquia, o repo de uma semana não representa todo o aperto de 2017–2018 via Late Liquidity Window. WACF é custo efetivo ponderado por taxas e volumes de financiamento do TCMB, não outro nome para repo. Nenhuma curva WACF foi estimada a partir da taxa oficial.

Em 2022, o TCMB descreve financiamento de mercado aberto via repo de uma semana; o descolamento relevante também envolvia crédito e títulos, sob exigências de reservas, manutenção de títulos e direcionamento de empréstimos. A liraização e os depósitos KKM afetavam incentivos, risco cambial e liquidez. A nota junto ao gráfico distingue esses canais e cita TCMB 2017, 2022, 2023 e o Artigo IV do FMI de 2022 publicado em 2023. Não se atribui todo o episódio a uma taxa observada isolada.

## Arquivos e fontes

`data/snapshot.json` contém todas as séries e proveniência, inclusive juros, OCDE, flags e componentes; `analysis.json`, somente cálculo/diagnósticos/comparação; `series.csv`, valores de todas as séries e áreas, com unidade, URL, consulta e status; `data.js`, snapshot mais análise para uso offline. Ausências são null no JSON e vazias no CSV, nunca zero. Há null mensal explícito nos juros sem observação. JSONs de análise/validação são gravados com LF explícito, independente do sistema operacional, para os hashes coincidirem na publicação. `.gitattributes` preserva os bytes das respostas brutas, CSV e arquivos de referência.

- WDI: https://api.worldbank.org/v2/; códigos e consultas em `config.py` e no snapshot.
- BIS: https://data.bis.org/topics/CBPOL; definições em https://www.bis.org/statistics/cbpol/cbpol_doc.pdf.
- OCDE: https://www.oecd.org/en/data/indicators/gdp-per-hour-worked.html e URLs SDMX completas por série; contexto em https://doi.org/10.1787/d01c660f-en.
- TCMB: https://www3.tcmb.gov.tr/yillikrapor/2017/en/m-2-1.php, https://www3.tcmb.gov.tr/yillikrapor/2022/en/m-2-2.html e https://www3.tcmb.gov.tr/yillikrapor/2023/en/m-2-2/.
- FMI: https://www.elibrary.imf.org/view/journals/002/2023/303/article-A001-en.xml, referência de interpretação, sem preencher lacunas de dados.
- Abadie, Diamond e Hainmueller (2010): https://economics.mit.edu/sites/default/files/publications/Synthetic%20Control%20Methods.pdf.
- SLSQP: https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html.

Sem imputação, interpolação, dessazonalização, winsorização ou combinação de observações com projeções. Linhas conectam observações para leitura e não estimam os intervalos. Inflação é média anual; câmbio é média oficial; PIB é crescimento real anual em colunas. Índice: 100×X/X2017; variação anual: 100×(X/Xanterior−1), apenas nas séries de nível apropriadas. A disponibilidade oficial não implica dado definitivo; flags provisórias e revisões são preservadas.

O relatório não fornece identificação causal, índice de diversificação exportadora, medida ambiental ou distributiva abrangente. Apache ECharts 5.6.0, licença Apache 2.0 em `vendor/LICENSE.txt`. Produzido com assistência do Codex, sem confirmação de troca da configuração do modelo. `RELATORIO_TECNICO.md` apresenta a revisão e `PUBLICACAO.md`, o registro de publicação.
