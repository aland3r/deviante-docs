# Parte III: Database First

## 1. Ferramenta escolhida

A demonstração usa o **Entity Framework Core 8** (EF Core), o ORM do .NET, com o provedor **Npgsql** para PostgreSQL, e o gerador de código do **ASP.NET Core MVC**. O banco fica no Supabase, o mesmo serviço de banco do projeto, num schema separado só para a demonstração.

| Ferramenta | Papel na abordagem Database First |
|---|---|
| `dotnet ef dbcontext scaffold` | Lê a estrutura do banco (tabelas, colunas, tipos, chaves, valores padrão e relacionamentos) e gera as classes de entidade e o contexto do EF Core |
| `dotnet aspnet-codegenerator controller` | A partir das classes geradas, cria o CRUD completo: um controller com listar, detalhar, criar, editar e excluir, e uma tela Razor para cada ação |
| Npgsql.EntityFrameworkCore.PostgreSQL | Provedor que permite ao EF Core ler e escrever no PostgreSQL |

A escolha atende aos três pontos do enunciado: gera as classes a partir do banco, gera o CRUD e gera as telas. No Database First o banco é a fonte da verdade: quando uma tabela muda, basta rodar o mesmo comando de novo para atualizar as classes e as telas. Isso é reuso gerativo: o esquema do banco é reaproveitado como ativo, e o código é produzido a partir dele em vez de escrito à mão.

## 2. Banco de dados

O schema `dbfirst` tem duas tabelas do domínio do Driftor, ligadas por chave estrangeira, com as quatro empresas clientes e seis máquinas de demonstração. Um usuário próprio do banco, com acesso restrito a esse schema, é usado pela aplicação.

| Tabela | Colunas | Regras definidas no banco |
|---|---|---|
| empresas | id, nome, cnpj, setor | Chave primária gerada pelo banco; CNPJ único |
| maquinas | id, empresa_id, nome, tag, tipo, situacao, criada_em | Chave estrangeira para empresas; situação padrão "ativa"; data de criação padrão = hoje |

## 3. Geração das classes

Comando executado num projeto ASP.NET Core MVC vazio:

```
dotnet ef dbcontext scaffold <conexão> Npgsql.EntityFrameworkCore.PostgreSQL --schema dbfirst --context DriftorContext --output-dir Models --context-dir Data --no-onconfiguring
```

| Arquivo gerado | O que foi gerado a partir do banco |
|---|---|
| Models/Empresa.cs | Uma propriedade por coluna de empresas e a coleção Maquinas, vinda da chave estrangeira |
| Models/Maquina.cs | Uma propriedade por coluna de maquinas (empresa_id virou EmpresaId) e a referência Empresa |
| Data/DriftorContext.cs | Mapeamento completo: nomes de tabelas e colunas, tamanhos máximos, CNPJ único, valores padrão e o relacionamento entre as tabelas |

O único código escrito à mão foi o registro do contexto na aplicação, em Program.cs, com a conexão lida da configuração.

## 4. Geração do CRUD e das telas

```
dotnet aspnet-codegenerator controller -name EmpresasController -m Empresa -dc DriftorContext --relativeFolderPath Controllers --useDefaultLayout
dotnet aspnet-codegenerator controller -name MaquinasController -m Maquina -dc DriftorContext --relativeFolderPath Controllers --useDefaultLayout
```

| Gerado | Conteúdo |
|---|---|
| Controllers/EmpresasController.cs e MaquinasController.cs | Ações Index, Details, Create, Edit e Delete, já usando o DriftorContext |
| Views/Empresas e Views/Maquinas | Cinco telas Razor por tabela: lista, detalhes, criação, edição e exclusão |

O cadastro de máquinas já traz a escolha da empresa, porque o gerador reconheceu a chave estrangeira. Os campos com valor padrão no banco (situação e data de criação) ficam de fora do formulário de criação e são preenchidos pelo próprio banco.

[Figura 2: Lista de máquinas gerada a partir do banco]

[Figura 3: Formulário de criação de máquina gerado a partir do banco]

## 5. Demonstração

A demonstração ao vivo é feita pelo aluno Alander Menezes Arantes de Ávila, numa pasta vazia, em seis passos: mostrar as tabelas no banco, criar o projeto MVC, gerar as classes, registrar o contexto, gerar o CRUD e as telas, e usar a aplicação para criar, editar e excluir uma máquina, conferindo cada mudança no banco.

Para mostrar que o banco é a fonte da verdade, a demonstração termina com uma mudança no banco: a coluna fabricante é acrescentada à tabela maquinas, os mesmos comandos são executados de novo e o campo aparece na classe Maquina e nas telas, sem edição manual do código.

O passo a passo completo, com os comandos e os problemas comuns, está no guia da demonstração, no repositório do projeto (pasta "Desenvolvimento Orientado a Reuso/database-first").
