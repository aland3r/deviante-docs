# Defesa Reuso 03: as 10 classes principais

O item 01 pede, antes dos padrões, ao menos 10 classes principais codificadas, com atributos e métodos. As dez abaixo estão no código que roda hoje. Cada link abre a definição da classe num commit fixo (`deviante-api@d6ab141`, `deviante-web@b69d9b5`).

| # | Classe | Linguagem e serviço | Atributos | Métodos | Papel no Deviante |
|---|---|---|---|---|---|
| 1 | [`AppConfig`](https://github.com/aland3r/deviante-api/blob/d6ab141/src/main/kotlin/AppConfig.kt#L14-L43) | Kotlin, Core | `jdbcUrl`, `dbUser`, `dbPassword`, `supabaseUrl`, `supabaseAnonKey`, `miningUrl`, `productLine`, `loaded` | `init(config)` | Configuração lida uma vez (Singleton) |
| 2 | [`ProductLine`](https://github.com/aland3r/deviante-api/blob/d6ab141/src/main/kotlin/variability/ProductLine.kt#L57-L90) | Kotlin, Core | `default`, `variants` | `variantForClient(client)`, `variantOrDefault(client)`, `fromConfig(config)` | Catálogo das variantes da linha de produto |
| 3 | [`ClientVariant`](https://github.com/aland3r/deviante-api/blob/d6ab141/src/main/kotlin/variability/ProductLine.kt#L47-L55) | Kotlin, Core | `client`, `plan`, `exclusive`, `features` | `has(feature)` | A variante de uma empresa: plano e funções exclusivas |
| 4 | [`CompanyScope`](https://github.com/aland3r/deviante-api/blob/d6ab141/src/main/kotlin/Routing.kt#L164-L167) | Kotlin, Core | `variant`, `businessId`, `seesAll`, `visibleBusinesses` | `sees(recordBusinessId)` | O que cada usuário enxerga, por empresa |
| 5 | [`ManagerRecord`](https://github.com/aland3r/deviante-api/blob/d6ab141/src/main/kotlin/model/ManagerRecord.kt#L6-L29) | Kotlin, Core | `id`, `userId`, `email`, `fullName`, `role`, `businessId`, `createdAt`, `updatedAt` | `isOwner()`, `canDelete()`, `keepsCatalog()` | Usuário, com o papel e a empresa |
| 6 | [`SupabaseAuthClient`](https://github.com/aland3r/deviante-api/blob/d6ab141/src/main/kotlin/SupabaseAuth.kt#L32-L72) | Kotlin, Core | `baseUrl`, `anonKey`, `client` | `verify(accessToken)` | Confere o token do login Google no Supabase Auth |
| 7 | [`MiningClient`](https://github.com/aland3r/deviante-api/blob/d6ab141/src/main/kotlin/MiningClient.kt#L145-L257) | Kotlin, Core | `baseUrl`, `client`, `logger` | `parse(fileName, content)`, `detect(...)`, `predictMaintenance(...)` | Chama o serviço de mineração |
| 8 | [`AnalysisEngine`](https://github.com/aland3r/deviante-api/blob/d6ab141/mining/app/analysis_engine.py#L11-L26) | Python, mining | `_instance`, `detector` | `get_instance()`, `run(values, delta, treatment)` | Motor único de análise de drift (Singleton) |
| 9 | [`IpddAdwinAdapter`](https://github.com/aland3r/deviante-api/blob/d6ab141/mining/app/drift_detector.py#L45-L71) | Python, mining | `METHOD` | `detect(values, delta, treatment)` | Envolve o IPDD/ADWIN da pesquisa (Adapter) |
| 10 | [`Subject`](https://github.com/aland3r/deviante-web/blob/b69d9b5/src/lib/subject.js#L6-L24) | JavaScript, web | `observers` | `subscribe(observer)`, `unsubscribe(observer)`, `notify(event)` | Base dos sujeitos do Observer |

Além dessas, o domínio tem as classes de registro e os repositórios do Core. Os registros são `ProcessRecord`, `ActivityRecord`, `OperationRecord`, `EventLogRecord` e `AnalysisRecord`, em `deviante-api/src/main/kotlin/model/`. Os repositórios são `ProcessRepository`, `ActivitiesRepository`, `MappingRepository`, `MaintenanceRepository` e outros, em `repository/`. Os CRUDs da defesa passam por eles.
