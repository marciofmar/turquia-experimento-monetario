# Publicação e validação

Site: https://marciofmar.github.io/turquia-experimento-monetario/

Repositório público: https://github.com/marciofmar/turquia-experimento-monetario

GitHub Pages configurado para a raiz de `main`, HTTPS obrigatório. Edição dos dados: 02/11/2026. Dados anuais até 2025 conforme indicador; juros mensais até setembro de 2026. Não há atualização automática.

## Evidências

- 3.547 verificações de integridade dos dados, correspondência com respostas WDI, SHA-256 dos arquivos originais, restrições dos pesos, previsões, RMSPE e convergência de otimização (KKT).
- JavaScript validado por `node --check`.
- 12 arquivos públicos com HTTP 200 e texto equivalente ao local, normalizando apenas CRLF/LF. Detalhes e hashes em `VALIDACAO.json`.
- Inspeção visual em 1280×900 e 390×844. Sem transbordamento horizontal da página; os quatro gráficos foram renderizados em SVG.
- Fluxos testados: PIB em colunas; câmbio com base 2017=100; inclusão da Nigéria e aviso de juros ausentes; conta corrente; filtros de anos com correção de intervalo invertido; P&D e cobertura; troca de resultado/grupo do controle sintético; exibição de desvios; tabela de valores com lacunas de 2026; download de CSV concluído.
- Descrições acessíveis dos gráficos em português; sem erros registrados no console durante os fluxos testados.
- Revisão visual corrigiu a posição da unidade nos gráficos, acrescentou anotações das mudanças monetárias e atualizou a referência do script para evitar cache antigo.

## Limites da entrega

O controle sintético é uma reconstrução nova e exploratória; o histórico não continha arquivos suficientes para uma reprodução exata. Ajustes prévios e validação são imperfeitos, especialmente nos controles europeus. Não há inferência causal, p-valor ou intervalo de confiança causal. Não se construiu um índice de diversificação exportadora sem série desagregada validada. A escolha de Sol médio não foi confirmada.

O arquivo de validação identifica o commit de conteúdo testado; commits posteriores podem acrescentar esta documentação sem modificar o relatório ou os cálculos.
