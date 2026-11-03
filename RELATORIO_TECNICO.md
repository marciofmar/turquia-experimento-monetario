# Revisão técnica: controle sintético e estrutura produtiva

Fechamento da coleta: 2026-11-03. Fontes originais, horários e hashes estão em `data/snapshot.json`.

## Arquivos modificados e criados

- Coleta e cálculo: `scripts/config.py`, `scripts/fetch_data.py`, `scripts/analyze.py`, `scripts/validate.py`, `scripts/report.py` e `requirements.txt`.
- Interface e documentação: `index.html`, `app.js`, `style.css`, `README.md`, `.gitignore`, `.gitattributes`, `PUBLICACAO.md` e registros de validação.
- Dados regenerados: `data/snapshot.json`, `data/analysis.json`, `data/series.csv`, `data/data.js`, `data/validation.json` e respostas originais WDI/BIS/OCDE.
- Referência preservada: `data/baseline/analysis-v1.json` e `data/baseline/snapshot-v1.json`, correspondentes à edição do commit `d88ee5e`.

## Comparação de ajuste e pesos

RMSPE em pontos percentuais. O resultado antigo é reapresentado e depois reestimado com dados novos. A comparação seguinte altera o pool; a última altera somente a especificação no mesmo pool principal completo. Pesos positivos acima de 0,01% são mostrados; arredondamento pode afetar a soma aparente.

| Desfecho | Etapa | RMSPE pré 2010–2020 | Pesos dos doadores |
|---|---|---:|---|
| Inflação | Edição anterior | 3,2598 | Romênia 25,13%; Nigéria 74,87% |
| Inflação | Pool antigo, dados novos, univariado | 3,2598 | Romênia 25,13%; Nigéria 74,87% |
| Inflação | Pool principal, univariado | 5,9981 | África do Sul 45,64%; Índia 54,36% |
| Inflação | Pool principal, multivariado | 6,0928 | México 36,87%; Índia 63,13% |
| PIB real | Edição anterior | 2,1731 | Nigéria 19,42%; Egito 19,31%; Gana 61,26% |
| PIB real | Pool antigo, dados novos, univariado | 2,1731 | Nigéria 19,42%; Egito 19,31%; Gana 61,26% |
| PIB real | Pool principal, univariado | 3,1761 | Polônia 6,23%; Brasil 27,68%; Índia 66,09% |
| PIB real | Pool principal, multivariado | 3,4606 | Polônia 3,21%; Brasil 18,35%; Malásia 4,25%; Chile 9,17%; Índia 45,44%; Tchéquia 19,58% |

A revisão não melhora o ajuste da trajetória turca. O novo padrão exige características produtivas e abandona a forte dependência anterior de Nigéria/Gana. O ajuste prévio piora, e a interpretação causal fica limitada. A similaridade produtiva de alguns preditores não torna os países controles não tratados nem garante suporte comum suficiente.

V é fixo: 0,5 para o histórico do desfecho e 0,5 para quatro covariáveis; no treino principal são cinco linhas do histórico com peso 0,10 e quatro covariáveis com peso 0,125. Não se otimizou V no pós. As fórmulas, escalas, perdas e equilíbrio por preditor estão no README e no JSON.

| Desfecho / pool / especificação | Elegíveis / candidatos | RMSPE pré | RMSPE holdout 2018–2020 | RMSPE pós 2022–2023 / pré |
|---|---:|---:|---:|---:|
| Inflação / principal / multivariate | 13/13 | 6,09 | 10,75 | 9,41 |
| Inflação / principal / univariate | 13/13 | 6,00 | 10,59 | 9,57 |
| Inflação / extended / multivariate | 15/16 | 4,48 | 9,35 | 10,95 |
| Inflação / extended / univariate | 16/16 | 3,26 | 8,63 | 14,00 |
| PIB / principal / multivariate | 13/13 | 3,46 | 4,65 | 0,19 |
| PIB / principal / univariate | 13/13 | 3,18 | 4,84 | 0,22 |
| PIB / extended / multivariate | 15/16 | 3,45 | 4,66 | 0,32 |
| PIB / extended / univariate | 16/16 | 2,10 | 3,57 | 0,41 |

O pool principal tem 13 candidatos e cobertura pré completa. O estendido acrescenta Nigéria, Egito e Gana. Nigéria não dispõe de FBCF nem abertura comercial em 2010–2020: é excluída do multivariado e permanece no univariado, com os anos e motivos registrados. Não houve preenchimento ou exclusão por resultado posterior.

Validação temporal, leave-one-out (W>1%) e placebos espaciais foram refeitos para cada especificação/pool. O holdout constrói preditores apenas até 2017; não usa 2018–2020 para obter médias, escalas ou pesos. Os placebos não são filtrados por conveniência do ajuste. Não há p-valor ou efeito causal identificado.

## Leitura estrutural da Turquia em 2021–2025

- FBCF / PIB: 28,39% em 2021 para 30,59% em 2025.
- Manufatura / PIB: 22,12% em 2021 para 16,84% em 2024.
- Exportações / PIB: 35,05% em 2021 para 24,85% em 2025.
- PIB por empregado: 3,61% de crescimento acumulado entre 2021 e 2025, em PPC constante de 2021.

O aumento do peso do investimento não foi acompanhado, nesses indicadores, por maior participação da manufatura ou das exportações. Isso reforça a necessidade de distinguir expansão agregada de transformação produtiva. Como as participações são razões nominais, a divergência também pode refletir preços relativos, câmbio e o denominador. Não prova queda de volume industrial, ineficiência do investimento ou efeito dos juros. Manufatura de 2025 permanece ausente.

A API de FBCF por ativo foi acessada na coleta completa. Os pares com numerador e total observados têm parcelas de máquinas/equipamentos e armas, habitação e outras construções. Para a Turquia, a resposta traz apenas o total; os componentes não foram inferidos. As parcelas são % da FBCF a preços correntes, não % do PIB e não um índice de qualidade. A cobertura por país/ano e os termos das razões estão no snapshot.

A série OCDE de PIB/hora da Turquia termina em 2021, embora o agregado oficial OCDE e alguns pares avancem. Não há base nesta série para confirmar evolução da produtividade por hora turca em 2022–2025. O PIB/empregado não separa horas, utilização e PTF; não se dividiram níveis com bases PPC distintas para estimar horas.

A nota monetária distingue repo, WACF, LLW, regras de liraização, crédito/títulos e depósitos KKM, com documentos do TCMB e do FMI. Não se criou curva WACF artificial.

## Validação e publicação

33331 verificações passaram: hashes/linhas originais, paridade CSV/navegador, V/W, KKT, predições, RMSPE, soluções convexas conhecidas, invariância de unidade e ausência de vazamento do futuro no treino.

A validação visual e do endereço publicado é registrada separadamente em `PUBLICACAO.md` e `VALIDACAO.json`.

Site: https://marciofmar.github.io/turquia-experimento-monetario/
Repositório: https://github.com/marciofmar/turquia-experimento-monetario
