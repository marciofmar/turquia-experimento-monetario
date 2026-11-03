# Turquia: crescer, a que custo?

Relatório econômico interativo, em português brasileiro. HTML, CSS e JavaScript estáticos, sem build, conta ou servidor de aplicação. Série visual principal de 2017–2026; controle sintético treinado com histórico de 2010–2020.

## Abrir

Abra `index.html` diretamente ou execute `python -m http.server 8787` nesta pasta. A biblioteca Apache ECharts 5.6.0 está incluída em `vendor/`; dados locais em `data/data.js`. O site não precisa de chamadas externas para desenhar os gráficos. Os links de fontes precisam de conexão.

## Reprodução

Python 3, somente biblioteca padrão:

```sh
python scripts/fetch_data.py
python scripts/analyze.py
python scripts/validate.py
```

O primeiro comando consulta fontes vivas e muda a edição: a data `retrieved` deve ser atualizada no script e os textos de cobertura revisados. Os dados atuais foram consultados em 02/11/2026. Não há agendamento de atualização.

`fetch_data.py`: WDI, dez indicadores para 12 países, 2010–2026; BIS WS_CBPOL, mensal. Respostas originais, SHA-256 e URLs estão em `data/`. `analyze.py` gera séries para o navegador, CSV completo e diagnósticos. Ausência permanece `null` no JSON e vazia no CSV, nunca zero.

## Controle sintético exploratório

Reconstrução nova: a conversa de origem não forneceu arquivos, pesos ou código para reprodução exata. Ajuste univariado separado para inflação média e crescimento real do PIB, pesos não negativos com soma 1. Objetivo: minimizar soma de quadrados dos desvios de 2010–2020. Gradiente projetado no simplex, inicialização uniforme, máximo 25.000 passos, tolerância de 1e-10 na mudança dos pesos. A divisão por escala numérica comum mantém o objetivo original. Não há padronização individual, intercepto ou extrapolação.

Três conjuntos: todos os 11 doadores; Europa (Polônia, Hungria, Tchéquia, Romênia, Sérvia); demais emergentes (Brasil, Chile, África do Sul, Nigéria, Egito, Gana). Os 12 países são os identificados no histórico recuperado. Validação temporal: ajuste 2010–2017 e avaliação 2018–2020. Sensibilidade: exclusão individual de doadores com peso >1%. Placebos espaciais: cada doador vira alvo, sem a Turquia nos controles. RMSPE pós usa 2022 e 2023; 2023 mistura regimes e terremotos. 2021 não entra no ajuste nem no RMSPE pós.

**Limites:** poucos anos e muitos doadores; pré-ajuste imperfeito e possibilidade de sobreajuste; seleção de países por histórico da conversa; controles sob políticas próprias; choques globais heterogêneos. Não há atribuição aleatória, p-valor, intervalo causal ou garantia de identificação. A razão RMSPE pós/pré é diagnóstico, não prova. A inflação turca prévia é mal aproximada pelos controles europeus. A implementação não substitui um desenho de pesquisa com controles de composição econômica e dados mensais.

## Tratamentos

- PIB: crescimento real anual, mostrado em colunas.
- Inflação: média anual, não dezembro/dezembro.
- Câmbio: média oficial anual, moeda local/US$; índices com base fixa 2017=100 permitem comparar variações proporcionais, sem inferir competitividade real.
- Juros: fim do mês, banco central/BIS, instrumentos nacionais distintos. Não há juros BIS para Nigéria, Egito e Gana neste conjunto. Repo de 2017 não resume todos os instrumentos de aperto turcos.
- Índice para séries de nível: 100×X/valor2017. Variação: 100×(X/Xanterior−1). Somente câmbio, produtividade e renda permitem indexação; a interface macro expõe câmbio.
- Sem imputação, interpolação, suavização, winsorização ou mistura com projeções. Linhas conectam pontos observados para apresentação, sem estimar meses intermediários. Os pontos anuais ficam em julho no eixo apenas para facilitar leitura da faixa de datas; são agregados do ano inteiro.
- Produtividade: PIB por empregado em PPC constante de 2021, não por hora/PTF. Emprego pode ser estimado pela OIT. P&D, alta tecnologia, indústria de transformação e investimento são proxies parciais, não um índice composto de desenvolvimento.
- Não há indicador de diversificação exportadora propriamente dita; participação de alta tecnologia não o substitui. Dados ambientais e distributivos não foram incorporados.

2025 vem de respostas WDI armazenadas, substituindo os placeholders anteriores, e não de cópia dos números da conversa. WDI pode revisar dados e incluir estimativas; cobertura não significa definitivo. 2026 anual está ausente; juros até setembro de 2026. Não se reproduz a alegação anterior de juros correntes em 36% sem série oficial confirmando-a.

## Fontes e créditos

- Banco Mundial WDI: https://api.worldbank.org/v2/ e códigos/URLs por indicador em `snapshot.json`; licenciamento em https://datacatalog.worldbank.org/public-licenses.
- BIS: https://data.bis.org/topics/CBPOL e https://www.bis.org/statistics/cbpol/cbpol_doc.pdf; proveniência dos bancos centrais em `data.js`, campo `metadata`.
- OCDE: https://doi.org/10.1787/d01c660f-en.
- FMI: https://www.elibrary.imf.org/view/journals/002/2026/043/article-A001-en.xml, referência analítica, não preenchimento de séries.
- Banco da Inglaterra e Banco do Canadá: transmissão monetária, links no relatório. Horizontes estruturais são exemplos didáticos, não médias estimadas.
- Apache ECharts 5.6.0, Apache License 2.0; copyright preservado no arquivo distribuído e licença em `vendor/LICENSE.txt`.

Produzido com assistência do Codex. A configuração Sol médio não foi confirmada nem alterada nesta sessão. Textos e cálculos são novos; referências não implicam endosso das instituições.

## Publicação

Site estático compatível com GitHub Pages (raiz do ramo `main`) ou Vercel sem framework. Não contém segredos ou dados pessoais. Os arquivos brutos permitem auditoria e aumentam o tamanho do repositório, sem serem necessários para desenhar os gráficos. `PUBLICACAO.md` registra o destino e a verificação quando concluídos.
