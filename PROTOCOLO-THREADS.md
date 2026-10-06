# Protocolo de trabalho compartilhado (arc42)

## Contexto

O arc42 do Deviante tem 12 seções, cada uma trabalhada em uma thread separada. Todas as threads leem e escrevem nas mesmas páginas. **Você não tem acesso ao que as outras threads conversaram.** O Notion e este repositório são a única memória compartilhada. Se não está lá, não existe.

## Fonte de verdade

- Em caso de divergência, vale o **Notion**: página [Arquitetura: arc42](https://www.notion.so/3f05fc724940819f8655fcd12d1312de), com 12 subpáginas, uma por seção.
- `architecture/arc42.md` é **gerado** a partir do Notion por `scripts/notion_to_md.py` (rotina de hora em hora, 08h–23h). Nunca edite esse arquivo à mão: a próxima sincronização sobrescreve.
- O site ([deviante.alander.io/documentacao](https://deviante.alander.io/documentacao)) lê o `arc42.md` da `main`. Um push na `main` publica.
- O Word da entrega é gerado do `arc42.md` só no congelamento. Nele entram apenas ajustes de formatação; texto volta para o Notion.
- Glossário: subpágina **12. Glossário** no Notion.
- Decisões (ADRs): subpágina **9. Decisões de Arquitetura** no Notion.
- Requisitos: banco **Requirements** no Notion (um requisito por linha, com o ID do Notion).
- Pendências: banco **Checklist** no Notion.
- Diagramas UML: a versão oficial são os arquivos do **Astah** neste repositório (`Deviante-Diagrams.asta`, `DVE-UML.asta`).
- OOUX/ORCA (objetos, CTAs, atributos, personas): a pasta `UX/` deste repositório.

## Repositório e versionamento

- Só existe a branch `main`. Commit direto na `main`, sem PR.
- Nenhuma thread publica a própria branch (`claude/*`) nem cria tags. Se uma branch escapar, avise com o link para ela ser apagada.
- No Notion, diagramas ficam como código Mermaid, sem imagens. O site e o gerador do Word renderizam o código.
- A pasta local `C:\gestalt\deviante\docs` (também o vault do Obsidian) e o repositório ficam sempre iguais, nos dois sentidos: o que é criado no PC (Astah, UX, notas) sobe para a `main`, e o que muda no GitHub desce para o PC. `C:\gestalt\deviante\atualizar-repos.ps1` faz as duas coisas. A configuração `.obsidian/` é local e não vai para o git.
- Nada é apagado da pasta local sem pedido explícito.

## Escopo desta thread

- Meu escopo: declare na primeira resposta qual seção (ou bloco de seções) você trabalha.
- Fora do meu escopo: todo o resto. Se eu pedir algo que mexa em outra seção, avise antes de editar.

## Antes de editar

1. Releia o trecho exato que vai alterar, direto do Notion, mesmo que já tenha lido antes nesta conversa. Não confie em versão em memória.
2. Leia também o glossário e os requisitos/ADRs para usar a terminologia e a numeração vigentes.
3. Verifique se existem referências cruzadas ao trecho (outras seções que o citam). Liste-as.

## Ao editar

4. Faça edições pontuais, na subpágina da seção. Nunca reescreva a página inteira.
5. Não renumere ADRs, requisitos (RF/RNF) ou seções existentes. Para criar um novo, consulte o último número usado e use o próximo. Cite decisões como "ADR 0N".
6. Se precisar de um termo novo, adicione ao glossário antes de usá-lo. Não invente sinônimos para termos já definidos.
7. Se a mudança remover ou alterar algo que outra seção referencia, **não** corrija a outra seção por conta própria. Registre a pendência (item 9) e me avise.
8. Siga o template e os exemplos de [docs.arc42.org](https://docs.arc42.org/home/). Texto enxuto, sem repetir o mesmo fato em várias seções. Nenhum nome de pessoa fora da tabela de stakeholders (§1.3) e da linha de autores.

## Decisões

9. Toda decisão relevante tomada na conversa deve ser gravada no Notion (ADR na §9 ou nota na seção) antes de a thread ser considerada concluída. Decisão que só existe no chat é considerada não tomada.
10. Se algo ficar em aberto, registre no Checklist do Notion: o que mudou, qual seção/thread precisa reagir e por quê.

## Ao finalizar cada etapa

11. Responda com este resumo curto:
    - Páginas e seções alteradas
    - Decisões gravadas (e onde)
    - Termos ou numerações novos criados
    - Seções fora do meu escopo que podem ficar inconsistentes
    - Pendências abertas
12. A rotina publica o `arc42.md` sozinha. Commit manual só para arquivos fora do `arc42.md` (scripts, README, diagramas avulsos), direto na `main`, com mensagem descritiva.

## Se houver conflito

13. Se a página estiver diferente do que você esperava, ou houver contradição entre o que peço e o que está documentado, pare e me mostre o conflito. Não resolva sozinho.

---

# Thread de consistência final (prompt separado)

Use somente na thread cuja função é revisar o documento inteiro.

```
Você é o revisor de consistência do arc42. Não escreva conteúdo novo.
Leia as 12 subpáginas do Notion e aponte, sem editar:
- termos divergentes para o mesmo conceito
- IDs duplicados ou saltados (ADR, RF, RNF)
- referências cruzadas quebradas
- diagramas que contradizem o texto
- decisões em ADRs que não aparecem refletidas nas seções
- itens do Checklist ainda não resolvidos
Entregue uma tabela: problema | onde | sugestão de correção.
```

---

# Aviso para threads já em andamento

```
A partir de agora, siga o protocolo em PROTOCOLO-THREADS.md (repo deviante-docs).
Leia o arquivo inteiro agora e me confirme em uma linha qual é o seu
escopo. Releia o protocolo sempre que eu avisar que ele mudou.
```
