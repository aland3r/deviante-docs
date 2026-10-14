# Datasets da Alfa

Os quatro logs de eventos sintéticos de manufatura do artigo do IPDD/ADWIN (Tabela 1), em XES. A empresa Alfa do login protótipo é configurada com eles: um processo por base, análise no modo bruto, δ = 0,002, só a atividade `Machine_Operating`.

| Arquivo | Cenário | Desvios esperados |
|---|---|---|
| `ST_20.xes` | estável, sem desvio | 0 |
| `DR_20.xes` | um desvio | 4 |
| `DR_MS_20.xes` | desvios com manutenção | 7 |
| `DR_MS_ST_20.xes` | cenário misto | 9 |

As seis atividades dos logs (`Machine_Operating`, `Raw_Material_Loading`, `Short_Downtime`, `Finished_Product_Unloading`, `Equipment_Failure`, `Maintenance`) já estão no catálogo da Alfa. Assim, o gestor consegue subir qualquer um destes arquivos e mapear os eventos sem criar atividades novas.

Na defesa de Reuso, o `DR_MS_ST_20.xes` é o arquivo do upload ao vivo.
