# Publicação: edição multivariada

Site: https://marciofmar.github.io/turquia-experimento-monetario/

Repositório: https://github.com/marciofmar/turquia-experimento-monetario

GitHub Pages serve a raiz de `main`, com HTTPS obrigatório. Coleta concluída em 03/11/2026; a data/hora de cada fonte está em `data/snapshot.json`.

A revisão inclui 17 países, 18 séries, pool principal de 13 pares e pool estendido de sensibilidade. O multivariado é o padrão; o univariado permanece selecionável. V é fixo e declarado, com 50% para histórico e 50% para quatro covariáveis.

## Evidências

- Pipeline executado do zero: coleta, cálculo, validação e geração do relatório técnico.
- 33.331 verificações passaram. Abrangem fontes originais, hashes, CSV, dados do navegador, W/V, equilíbrio, KKT, previsões, RMSPE, invariância de unidade, soluções convexas conhecidas e ausência de vazamento temporal.
- A coleta mantém respostas em memória até concluir, preservando a edição anterior se uma fonte falhar. Ausências continuam nulas; não houve interpolação ou imputação.
- Inspeção visual local em 1280×900 e 390×844, com cinco gráficos SVG e sem transbordamento horizontal da página.
- As oito combinações de desfecho/pool/especificação foram exercitadas. Os diagnósticos vistos na interface conferem com a análise final.
- Conferidos os painéis por hora e por ativo com lacunas, o agregado oficial OCDE, a troca de país no painel conjunto e a abertura da nota repo/WACF/LLW/KKM.
- Nenhum erro de execução registrado no navegador durante esses fluxos. Evidência manual em `data/browser-validation.json`.
- A versão pública foi aberta no navegador: 17 países, multivariado padrão e alternância para univariado conferidos, sem erros registrados.
- 22 arquivos públicos responderam HTTP 200 e conferiram com o checkout. JSONs de análise, snapshot e validação, respostas brutas e CSV foram comparados em bytes. `scripts/verify_public.py` compara os arquivos HTTP com o checkout: respostas originais e CSV em bytes; outros textos com normalização CRLF/LF. O resultado, horários, hashes e commit de conteúdo testado ficam em `VALIDACAO.json`. Esse script não refaz os testes visuais.

## Limites

O novo padrão tem RMSPE pré pior que a edição anterior; não se apresenta o refinamento como melhoria de ajuste ou identificação causal. V não é estimado por busca aninhada. A Nigéria permanece no estendido univariado e é excluída do multivariado por ausência de FBCF e abertura no pré. A resposta de FBCF por ativo traz componentes de pares, mas só o total para a Turquia. O PIB por hora turco termina em 2021. Nenhuma dessas lacunas foi preenchida.

A comparação entre versões e a interpretação estrutural estão em `RELATORIO_TECNICO.md`; a formulação exata e os passos de reprodução, em `README.md`. A referência da edição anterior foi preservada em `data/baseline/` e no histórico Git. Commits posteriores podem registrar a verificação pública sem alterar os cálculos ou a interface testada.
