# Defesa Reuso 03: roteiro da Emanuelle (Equipamento e Agenda de manutenção)

Prova de autoria em 16/10. Cada integrante demonstra 2 CRUDs com conexão ao banco e explica o caminho do código. Este roteiro cobre **Equipamento** (máquina) e **Agenda de manutenção**. Os dois rodam só no Core (React → Ktor → Supabase Postgres), sem Function nem microsserviços.

**Como ler.** Cada trecho de código traz a localização exata: repositório, arquivo, linhas e um link fixo no commit (`deviante-api@1b5106c`, `deviante-web@203e38d`), que não muda mesmo que a `main` ande. Abaixo de cada trecho vem o que falar. Os blocos marcados **A DESENVOLVER** ainda não existem no código: trazem o código proposto e o lugar exato onde entra; depois do desenvolvimento, troque o bloco pelo link real.

## 0. Mapa do sistema

| Peça | Onde roda | Endereço | Código |
|---|---|---|---|
| Telas | Vercel | `https://deviante.alander.io` (`/equipment`, `/schedules`) | `aland3r/deviante-web` |
| Proxy da API | Vercel (rewrite) | `https://deviante.alander.io/api/*` → `https://deviante-api.fly.dev/api/*` | `deviante-web/vercel.json` |
| Core API | Fly.io, app `deviante-api`, região `iad` | `https://deviante-api.fly.dev/api` | `aland3r/deviante-api` (`src/main/kotlin`) |
| Autenticação | Supabase Auth (Google e contas demo) | `https://<projeto>.supabase.co/auth/v1/user` | chamado por `SupabaseAuth.kt` |
| Banco | Supabase Postgres, schema `deviante` | tabelas `equipment`, `maintenance_schedules`, `managers`, `users` | mapeado em `src/main/kotlin/db/*.kt` |
| Mining (não usado nos CRUDs) | Fly.io, app `deviante-mining` | só o Core chama | `deviante-api/mining/` |

Menu do sistema, onde ficam as duas telas:

📍 `deviante-web/src/components/layout/AppLayout.jsx` · linhas 28–33 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/components/layout/AppLayout.jsx#L28-L33)

```jsx
          {[
            ['/dashboard', 'Projetos'],
            ['/operations', 'Operações'],
            ['/equipment', 'Equipamentos'],
            ['/schedules', 'Agendamentos'],
          ].map(([to, label]) => (
```

📍 `deviante-web/vercel.json` · linhas 1–6 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/vercel.json#L1-L6)

```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://deviante-api.fly.dev/api/$1" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

O navegador sempre chama `/api/...` no próprio domínio do site; a Vercel repassa para o Fly.io. Por isso o front não precisa saber o endereço do Core.

## 1. O caminho comum (falar uma vez, no início)

```mermaid
sequenceDiagram
    actor M as Manager
    participant W as deviante-web (React)
    participant V as Vercel (rewrite /api)
    participant C as Core API (Ktor, Fly.io)
    participant A as Supabase Auth
    participant R as MaintenanceRepository (Exposed)
    participant DB as Postgres (schema deviante)
    M->>W: ação na tela
    W->>W: api.js request() anexa Bearer token
    W->>V: HTTPS /api/equipment ou /api/schedules
    V->>C: repassa para deviante-api.fly.dev
    C->>C: CORS (Http.kt) e JSON (Serialization.kt)
    C->>A: SupabaseAuthClient.verify(token)
    A-->>C: id e e-mail
    C->>R: ManagerRepository.findOrCreateForSupabaseUser
    C->>R: createEquipment / listSchedules / ...
    R->>DB: transaction { SQL }
    DB-->>R: linhas
    R-->>C: EquipmentResponse / MaintenanceScheduleResponse
    C-->>W: JSON
    W-->>M: lista recarregada
```

### 1.1 Front: o cliente HTTP

📍 `deviante-web/src/lib/api.js` · linhas 27–27 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/lib/api.js#L27-L27)

```javascript
const API_BASE = import.meta.env.VITE_API_URL ?? '/api'
```

📍 `deviante-web/src/lib/api.js` · linhas 243–267 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/lib/api.js#L243-L267)

```javascript
async function authHeader() {
  if (!isSupabaseConfigured()) return {}
  const { data } = await getSupabase().auth.getSession()
  const token = data.session?.access_token
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(await authHeader()),
      ...(options.headers ?? {}),
    },
    ...options,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new ApiError(payload.message ?? 'Falha na requisição.', payload.fieldErrors ?? {})
  }

  if (response.status === 204) return null
  return response.json()
}
```

Fala: "Toda chamada passa por `request()`. Ele pega o token da sessão do Supabase (`authHeader`) e manda no cabeçalho `Authorization: Bearer`. Se a resposta não for 2xx, transforma o JSON de erro num `ApiError`; se for 204, devolve `null`."

### 1.2 Core: inicialização

📍 `deviante-api/src/main/resources/application.yaml` · linhas 1–18 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/resources/application.yaml#L1-L18)

```yaml
ktor:
  deployment:
    port: 8080
  application:
    modules:
      - com.deviante.HttpKt.configureHttp
      - com.deviante.SerializationKt.configureSerialization
      - com.deviante.DatabaseKt.configureDatabase
      - com.deviante.RoutingKt.configureRouting

database:
  jdbcUrl: ${DATABASE_JDBC_URL:jdbc:postgresql://localhost:5432/postgres?sslmode=require}
  user: ${DATABASE_USER:postgres}
  password: ${DATABASE_PASSWORD:}

supabase:
  url: ${SUPABASE_URL:}
  anonKey: ${SUPABASE_ANON_KEY:}
```

📍 `deviante-api/src/main/kotlin/Http.kt` · linhas 8–24 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Http.kt#L8-L24)

```kotlin
fun Application.configureHttp() {
    install(CORS) {
        allowMethod(HttpMethod.Get)
        allowMethod(HttpMethod.Post)
        allowMethod(HttpMethod.Put)
        allowMethod(HttpMethod.Delete)
        allowMethod(HttpMethod.Patch)
        allowMethod(HttpMethod.Options)

        allowHeader(HttpHeaders.Authorization)
        allowHeader(HttpHeaders.ContentType)
        allowHeader(HttpHeaders.Accept)

        allowCredentials = true
        anyHost()
    }
}
```

📍 `deviante-api/src/main/kotlin/Database.kt` · linhas 9–27 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Database.kt#L9-L27)

```kotlin
fun Application.configureDatabase() {
    val jdbcUrl = environment.config.property("database.jdbcUrl").getString()
    val user = environment.config.property("database.user").getString()
    val password = environment.config.property("database.password").getString()

    val hikariConfig = HikariConfig().apply {
        this.jdbcUrl = jdbcUrl
        this.username = user
        this.password = password
        driverClassName = "org.postgresql.Driver"
        maximumPoolSize = 5
    }

    val dataSource = HikariDataSource(hikariConfig)
    Database.connect(dataSource)

    // Seed demo data if needed (idempotent check inside)
    SeedDemoData.runIfNeeded()
}
```

Fala: "O Ktor sobe os módulos nesta ordem: CORS, JSON, banco e rotas. O Hikari mantém um pool de até 5 conexões com o Postgres; o Exposed usa esse pool em cada `transaction { }`."

### 1.3 Core: autenticação e Manager

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 107–121 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L107-L121)

```kotlin
private suspend fun ApplicationCall.requireSupabaseUser(authClient: SupabaseAuthClient): SupabaseUser? {
    val header = request.headers[HttpHeaders.Authorization]
    val token = header?.removePrefix("Bearer ")?.trim()
    if (token.isNullOrBlank()) {
        respond(HttpStatusCode.Unauthorized, ErrorResponse("Você precisa estar autenticado."))
        return null
    }

    val user = authClient.verify(token)
    if (user == null) {
        respond(HttpStatusCode.Unauthorized, ErrorResponse("Sessão inválida ou expirada."))
        return null
    }
    return user
}
```

📍 `deviante-api/src/main/kotlin/SupabaseAuth.kt` · linhas 44–71 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/SupabaseAuth.kt#L44-L71)

```kotlin
    /** Verifies a Supabase access token by asking Supabase Auth who it belongs to. */
    suspend fun verify(accessToken: String): SupabaseUser? {
        if (baseUrl.isBlank() || anonKey.isBlank()) {
            logger.error("Supabase auth is not configured (SUPABASE_URL / SUPABASE_ANON_KEY missing).")
            return null
        }

        return try {
            val response = client.get("$baseUrl/auth/v1/user") {
                header(HttpHeaders.Authorization, "Bearer $accessToken")
                header("apikey", anonKey)
            }
            if (!response.status.isSuccess()) {
                logger.warn("Supabase rejected the access token: {} {}", response.status, response.bodyAsText())
                return null
            }

            val body = response.body<SupabaseUserResponse>()
            SupabaseUser(
                id = UUID.fromString(body.id),
                email = body.email ?: "",
                fullNameHint = body.user_metadata?.full_name ?: body.user_metadata?.name ?: "",
            )
        } catch (error: Exception) {
            logger.error("Failed to verify Supabase access token.", error)
            null
        }
    }
```

📍 `deviante-api/src/main/kotlin/repository/ManagerRepository.kt` · linhas 42–62 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/ManagerRepository.kt#L42-L62)

```kotlin
    fun findOrCreateForSupabaseUser(supabaseUserId: UUID, email: String, fullNameHint: String): ManagerRecord =
        transaction {
            val existing = (ManagersTable innerJoin UsersTable)
                .selectAll()
                .where { ManagersTable.userId eq supabaseUserId }
                .limit(1)
                .firstOrNull()
                ?.toManagerRecord()
            if (existing != null) {
                // Re-derive the role on every login: a manager row created
                // before its e-mail was added to OWNER_EMAILS/MENTOR_EMAILS
                // would otherwise stay stuck on the role it got at signup.
                val expected = detectRole(existing.email)
                if (existing.role == expected) return@transaction existing

                ManagersTable.update({ ManagersTable.userId eq supabaseUserId }) {
                    it[ManagersTable.role] = expected
                    it[ManagersTable.updatedAt] = OffsetDateTime.now()
                }
                return@transaction existing.copy(role = expected)
            }
```

Fala: "O Core pergunta ao Supabase Auth de quem é o token (401 se não houver ou se for inválido) e acha ou cria a linha do Manager. O `manager.id` é o que vai em `equipment.manager_id`."

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 1514–1518 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L1514-L1518)

```kotlin
private fun runCatchingUuid(value: String): UUID? = try {
    UUID.fromString(value)
} catch (_: IllegalArgumentException) {
    null
}
```

## 2. CRUD de Equipamento (objeto ORCA MACHINE)

### 2.1 Tabela e DTOs

📍 `deviante-api/src/main/kotlin/db/MonitoringTables.kt` · linhas 6–24 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/db/MonitoringTables.kt#L6-L24)

```kotlin
object EquipmentTable : Table(name = "equipment") {
    override val tableName = "deviante.equipment"
    val id = uuid("id")
    val managerId = uuid("manager_id").references(ManagersTable.id).nullable()
    val name = varchar("name", 150)
    val tag = varchar("tag", 100).nullable()
    val kind = varchar("kind", 100).nullable()
    val location = varchar("location", 200).nullable()
    val description = text("description")
    val manufacturer = varchar("manufacturer", 150).nullable()
    val model = varchar("model", 150).nullable()
    val serialNumber = varchar("serial_number", 150).nullable()
    val status = varchar("status", 30)
    val assetUrl = text("asset_url").nullable()
    val assetFormat = varchar("asset_format", 20).nullable()
    val createdAt = timestampWithTimeZone("created_at")
    val updatedAt = timestampWithTimeZone("updated_at")
    override val primaryKey = PrimaryKey(id)
}
```

📍 `deviante-api/src/main/kotlin/dto/MaintenanceDto.kt` · linhas 6–48 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/dto/MaintenanceDto.kt#L6-L48)

```kotlin
@Serializable
data class EquipmentRequest(
    val name: String,
    val tag: String? = null,
    val kind: String? = null,
    val location: String? = null,
    val description: String = "",
    val manufacturer: String? = null,
    val model: String? = null,
    val serialNumber: String? = null,
    val status: String = "active",
    val assetUrl: String? = null,
    val assetFormat: String? = null,
)

@Serializable
data class EquipmentResponse(
    val id: String,
    val name: String,
    val tag: String? = null,
    val kind: String? = null,
    val location: String? = null,
    val description: String,
    val manufacturer: String? = null,
    val model: String? = null,
    val serialNumber: String? = null,
    val status: String,
    val assetUrl: String? = null,
    val assetFormat: String? = null,
    val createdAt: String,
    val updatedAt: String,
    val processIds: List<String> = emptyList(),
    val processNames: List<String> = emptyList(),
    val monitoringIds: List<String> = emptyList(),
    val monitoringNames: List<String> = emptyList(),
    val parameterCount: Int = 0,
    val readingCount: Int = 0,
    val analysisCount: Int = 0,
    val latestRulValue: Double? = null,
    val latestRulUnit: String? = null,
    val latestFailureProbability: Double? = null,
    val latestAnalysisAt: String? = null,
)
```

Fala: "Só `name` é obrigatório no `EquipmentRequest`. A resposta traz, além das colunas, os nomes dos processos e monitoramentos ligados. No banco, apagar um equipamento apaga em cascata as agendas, vínculos com processos e monitoramentos, parâmetros e recomendações (conferido no Supabase em 13/10)."

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 381–391 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L381-L391)

```kotlin
    private fun assignEquipment(row: UpdateBuilder<*>, body: EquipmentRequest) {
        row[EquipmentTable.name] = body.name.trim(); row[EquipmentTable.description] = body.description.trim()
        row[EquipmentTable.tag] = body.tag?.trim()?.takeIf(String::isNotBlank)
        row[EquipmentTable.kind] = body.kind?.trim()?.takeIf(String::isNotBlank)
        row[EquipmentTable.location] = body.location?.trim()?.takeIf(String::isNotBlank)
        row[EquipmentTable.manufacturer] = body.manufacturer?.trim()?.takeIf(String::isNotBlank)
        row[EquipmentTable.model] = body.model?.trim()?.takeIf(String::isNotBlank)
        row[EquipmentTable.serialNumber] = body.serialNumber?.trim()?.takeIf(String::isNotBlank)
        row[EquipmentTable.status] = body.status; row[EquipmentTable.assetUrl] = body.assetUrl?.trim()?.takeIf(String::isNotBlank)
        row[EquipmentTable.assetFormat] = body.assetFormat?.trim()?.takeIf(String::isNotBlank)
    }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 399–399 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L399-L399)

```kotlin
    private fun equipment(r: ResultRow) = EquipmentResponse(r[EquipmentTable.id].toString(), r[EquipmentTable.name], r[EquipmentTable.tag], r[EquipmentTable.kind], r[EquipmentTable.location], r[EquipmentTable.description], r[EquipmentTable.manufacturer], r[EquipmentTable.model], r[EquipmentTable.serialNumber], r[EquipmentTable.status], r[EquipmentTable.assetUrl], r[EquipmentTable.assetFormat], r[EquipmentTable.createdAt].iso(), r[EquipmentTable.updatedAt].iso())
```

Fala: "`assignEquipment` é reaproveitada no insert e no update: limpa espaços e grava `null` no que veio vazio. `equipment(r)` transforma a linha em DTO."

### 2.2 Create — tela `/equipment`, botão "Novo equipamento"

📍 `deviante-web/src/pages/EquipmentPage.jsx` · linhas 36–38 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/pages/EquipmentPage.jsx#L36-L38)

```jsx
  const actions = <button onClick={() => setCreating(true)} className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold text-white" style={{ background: 'var(--ok-strong)' }}><Plus size={12} />Novo equipamento</button>
  return <Surface title="Equipamentos" subtitle={`${rows.length} ativos cadastrados com histórico, análises e vínculos.`} icon={Cpu} actions={actions}>
    {creating && <CreateEquipmentModal onClose={() => setCreating(false)} onCreate={async (data) => { await api.createEquipment(data); setCreating(false); load() }} />}
```

📍 `deviante-web/src/pages/EquipmentPage.jsx` · linhas 88–92 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/pages/EquipmentPage.jsx#L88-L92)

```jsx
function CreateEquipmentModal({ onClose, onCreate }) {
  const [values, setValues] = useState({ name: '', kind: 'generico', tag: '', location: '', manufacturer: '', model: '' }); const [busy, setBusy] = useState(false)
  const field = (key, placeholder) => <input value={values[key]} onChange={(event) => setValues((current) => ({ ...current, [key]: event.target.value }))} placeholder={placeholder} className="px-3 py-2 rounded-lg border border-border text-xs text-foreground" style={{ background: 'var(--surface-base)' }} />
  return <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(3,6,12,.78)' }}><form onSubmit={async (event) => { event.preventDefault(); if (!values.name.trim()) return; setBusy(true); try { await onCreate(values) } finally { setBusy(false) } }} className="w-full rounded-xl border border-border" style={{ maxWidth: 480, background: 'var(--surface-raised)' }}><div className="flex justify-between px-4 py-3 border-b border-border"><div><h2 className="text-sm font-semibold text-foreground">Cadastrar equipamento</h2><p className="text-[11px] text-muted-foreground mt-1">Crie o ativo antes de associá-lo a processos ou monitoramentos.</p></div><button type="button" onClick={onClose}><X size={13} /></button></div><div className="grid gap-3 p-4 sm:grid-cols-2"><label className="flex flex-col gap-1 text-[10px] text-muted-foreground sm:col-span-2">Nome *{field('name', 'Ex.: Torno CNC Prod1')}</label><label className="flex flex-col gap-1 text-[10px] text-muted-foreground">Tipo<select value={values.kind} onChange={(event) => setValues((current) => ({ ...current, kind: event.target.value }))} className="px-3 py-2 rounded-lg border border-border text-xs text-foreground" style={{ background: 'var(--surface-base)' }}><option value="torno">Torno CNC</option><option value="fresadora">Fresadora</option><option value="compressor">Compressor</option><option value="esteira">Esteira</option><option value="generico">Genérico</option></select></label><label className="flex flex-col gap-1 text-[10px] text-muted-foreground">TAG{field('tag', 'Ex.: TRN-01')}</label><label className="flex flex-col gap-1 text-[10px] text-muted-foreground">Fabricante{field('manufacturer', 'Ex.: Romi')}</label><label className="flex flex-col gap-1 text-[10px] text-muted-foreground">Modelo{field('model', 'Ex.: GL 240')}</label><label className="flex flex-col gap-1 text-[10px] text-muted-foreground sm:col-span-2">Localização{field('location', 'Ex.: Célula 01')}</label></div><div className="flex justify-end gap-2 px-4 py-3 border-t border-border"><button type="button" onClick={onClose} className="px-3 py-2 text-xs text-muted-foreground">Cancelar</button><button disabled={busy || !values.name.trim()} className="px-3 py-2 rounded-lg text-xs font-semibold text-white disabled:opacity-50" style={{ background: 'var(--ok-strong)' }}>{busy ? 'Cadastrando…' : 'Cadastrar'}</button></div></form></div>
}
```

📍 `deviante-web/src/lib/api.js` · linhas 488–488 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/lib/api.js#L488-L488)

```javascript
  createEquipment: (data) => request('/equipment', { method: 'POST', body: JSON.stringify(data) }),
```

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 454–460 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L454-L460)

```kotlin
                post {
                    val user = call.requireSupabaseUser(authClient) ?: return@post
                    val manager = managerRepository.findOrCreateForSupabaseUser(user.id, user.email, user.fullNameHint)
                    val body = call.receive<EquipmentRequest>()
                    if (body.name.isBlank()) { call.respond(HttpStatusCode.BadRequest, ErrorResponse("Nome do equipamento é obrigatório.")); return@post }
                    call.respond(HttpStatusCode.Created, maintenanceRepository.createEquipment(manager.id, body))
                }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 100–107 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L100-L107)

```kotlin
    fun createEquipment(managerId: UUID, body: EquipmentRequest): EquipmentResponse = transaction {
        val id = UUID.randomUUID(); val now = OffsetDateTime.now()
        EquipmentTable.insert {
            it[EquipmentTable.id] = id; it[EquipmentTable.managerId] = managerId
            assignEquipment(it, body); it[EquipmentTable.createdAt] = now; it[EquipmentTable.updatedAt] = now
        }
        findEquipment(id)!!
    }
```

Fala: "O modal só habilita 'Cadastrar' com nome preenchido. A rota valida de novo (400 'Nome do equipamento é obrigatório') e o repositório gera o UUID, grava o `manager_id` de quem está logado e devolve a linha recém-criada (201)."

### 2.3 Read — tela `/equipment`

📍 `deviante-web/src/pages/EquipmentPage.jsx` · linhas 9–19 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/pages/EquipmentPage.jsx#L9-L19)

```jsx
export default function EquipmentPage() {
  const [rows, setRows] = useState([])
  const [query, setQuery] = useState('')
  const [processId, setProcessId] = useState('')
  const [monitoringId, setMonitoringId] = useState('')
  const [health, setHealth] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const load = () => api.listAllMachines().then((data) => setRows(Array.isArray(data) ? data : data?.items ?? [])).catch((err) => setError(err instanceof ApiError ? err.message : 'Não foi possível carregar os equipamentos.')).finally(() => setLoading(false))
  useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps
```

📍 `deviante-web/src/lib/api.js` · linhas 487–487 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/lib/api.js#L487-L487)

```javascript
  listAllMachines: () => request('/equipment'),
```

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 449–453 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L449-L453)

```kotlin
                get {
                    val user = call.requireSupabaseUser(authClient) ?: return@get
                    val manager = managerRepository.findOrCreateForSupabaseUser(user.id, user.email, user.fullNameHint)
                    call.respond(maintenanceRepository.listEquipment(manager.id))
                }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 48–55 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L48-L55)

```kotlin
    fun listEquipment(managerId: UUID): List<EquipmentResponse> = transaction {
        val rows = EquipmentTable.selectAll()
            .where { EquipmentTable.managerId eq managerId }
            .orderBy(EquipmentTable.updatedAt, SortOrder.DESC)
            .toList()
        if (rows.isEmpty()) return@transaction emptyList()
        val equipmentIds = rows.map { it[EquipmentTable.id] }

```

Fala: "A lista filtra pelo `manager_id` de quem está logado, então cada gestor só vê os próprios equipamentos. Os filtros da tela (busca, processo, monitoramento) rodam no navegador sobre essa lista."

Read de um equipamento:

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 461–466 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L461-L466)

```kotlin
                get("/{id}") {
                    call.requireSupabaseUser(authClient) ?: return@get
                    val id = call.parameters["id"]?.let(::runCatchingUuid)
                    val item = id?.let(maintenanceRepository::findEquipment)
                    if (item == null) call.respond(HttpStatusCode.NotFound, ErrorResponse("Equipamento não encontrado.")) else call.respond(item)
                }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 96–98 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L96-L98)

```kotlin
    fun findEquipment(id: UUID): EquipmentResponse? = transaction {
        EquipmentTable.selectAll().where { EquipmentTable.id eq id }.firstOrNull()?.let(::equipment)
    }
```

### 2.4 Update — já existe na API

📍 `deviante-web/src/lib/api.js` · linhas 469–471 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/lib/api.js#L469-L471)

```javascript
  updateMachine: (machineId, patch) => request(`/equipment/${machineId}`, {
    method: 'PUT', body: JSON.stringify(patch),
  }),
```

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 467–474 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L467-L474)

```kotlin
                put("/{id}") {
                    call.requireSupabaseUser(authClient) ?: return@put
                    val id = call.parameters["id"]?.let(::runCatchingUuid)
                    val body = call.receive<EquipmentRequest>()
                    if (id == null || body.name.isBlank()) { call.respond(HttpStatusCode.BadRequest, ErrorResponse("Equipamento ou nome inválido.")); return@put }
                    val item = maintenanceRepository.updateEquipment(id, body)
                    if (item == null) call.respond(HttpStatusCode.NotFound, ErrorResponse("Equipamento não encontrado.")) else call.respond(item)
                }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 109–112 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L109-L112)

```kotlin
    fun updateEquipment(id: UUID, body: EquipmentRequest): EquipmentResponse? = transaction {
        if (EquipmentTable.update({ EquipmentTable.id eq id }) { assignEquipment(it, body); it[EquipmentTable.updatedAt] = OffsetDateTime.now() } == 0) null
        else findEquipment(id)
    }
```

Fala: "Se o `UPDATE` não alterou nenhuma linha, o repositório devolve `null` e a rota responde 404."

### 2.5 Delete — já existe na API

📍 `deviante-web/src/lib/api.js` · linhas 472–472 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/lib/api.js#L472-L472)

```javascript
  deleteMachine: (machineId) => request(`/equipment/${machineId}`, { method: 'DELETE' }),
```

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 475–480 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L475-L480)

```kotlin
                delete("/{id}") {
                    call.requireSupabaseUser(authClient) ?: return@delete
                    val id = call.parameters["id"]?.let(::runCatchingUuid)
                    if (id == null || !maintenanceRepository.deleteEquipment(id)) call.respond(HttpStatusCode.NotFound, ErrorResponse("Equipamento não encontrado."))
                    else call.respond(HttpStatusCode.NoContent)
                }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 114–114 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L114-L114)

```kotlin
    fun deleteEquipment(id: UUID): Boolean = transaction { EquipmentTable.deleteWhere { EquipmentTable.id eq id } > 0 }
```

### 2.6 A DESENVOLVER: editar e excluir na tela `/equipment`

Hoje `api.updateMachine` e `api.deleteMachine` existem, mas nenhuma tela os chama.

📍 `deviante-web/src/pages/EquipmentPage.jsx`, novo estado depois da linha 17:

```jsx
  const [editing, setEditing] = useState(null)
  async function removeMachine(machine) {
    if (!window.confirm(`Excluir "${machine.name}"? As agendas dele também serão apagadas.`)) return
    try { await api.deleteMachine(machine.id); load() } catch (err) { setError(err instanceof ApiError ? err.message : 'Não foi possível excluir.') }
  }
```

📍 mesmo arquivo, depois da linha 38 (o modal de criar), o mesmo modal no modo edição:

```jsx
    {editing && <CreateEquipmentModal initial={editing} onClose={() => setEditing(null)} onCreate={async (data) => { await api.updateMachine(editing.id, data); setEditing(null); load() }} />}
```

📍 mesmo arquivo, linha 50: acrescentar `<Header>Ações</Header>` ao fim do cabeçalho; linha 61: nova célula no fim de cada linha:

```jsx
            <Cell><button onClick={() => setEditing(machine)}>Editar</button> · <button onClick={() => removeMachine(machine)}>Excluir</button></Cell>
```

📍 mesmo arquivo, linha 88–89: o modal passa a aceitar valores iniciais:

```jsx
function CreateEquipmentModal({ onClose, onCreate, initial }) {
  const [values, setValues] = useState({ name: initial?.name ?? '', kind: initial?.kind ?? 'generico', tag: initial?.tag ?? '', location: initial?.location ?? '', manufacturer: initial?.manufacturer ?? '', model: initial?.model ?? '' }); const [busy, setBusy] = useState(false)
```

(no título do modal, trocar "Cadastrar equipamento" por `{initial ? 'Editar equipamento' : 'Cadastrar equipamento'}`).

### 2.7 Roteiro de fala

1. Logar e abrir `https://deviante.alander.io/equipment`.
2. **Create:** cadastrar "Torno CNC Prod1", tipo torno, TAG TRN-01. Mostrar no DevTools o `POST /api/equipment` e o 201.
3. **Read:** mostrar a lista e o `WHERE manager_id = ?` no repositório.
4. **Update:** editar a localização (`PUT /api/equipment/{id}`).
5. **Delete:** excluir um equipamento sem agenda (204). Explicar que, com agenda, o banco apaga a agenda junto (cascata).

## 3. CRUD de Agenda de manutenção (objeto ORCA MAINTENANCE)

### 3.1 Tabela e DTOs

📍 `deviante-api/src/main/kotlin/db/MonitoringTables.kt` · linhas 142–157 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/db/MonitoringTables.kt#L142-L157)

```kotlin
object MaintenanceSchedulesTable : Table(name = "maintenance_schedules") {
    override val tableName = "deviante.maintenance_schedules"
    val id = uuid("id")
    val equipmentId = uuid("equipment_id").references(EquipmentTable.id)
    val processId = uuid("process_id").references(ProcessesTable.id).nullable()
    val recommendationId = uuid("recommendation_id").references(MaintenanceRecommendationsTable.id).nullable()
    val managerId = uuid("manager_id").references(ManagersTable.id)
    val title = varchar("title", 200)
    val notes = text("notes")
    val scheduledStart = timestampWithTimeZone("scheduled_start")
    val scheduledEnd = timestampWithTimeZone("scheduled_end").nullable()
    val status = varchar("status", 30)
    val createdAt = timestampWithTimeZone("created_at")
    val updatedAt = timestampWithTimeZone("updated_at")
    override val primaryKey = PrimaryKey(id)
}
```

📍 `deviante-api/src/main/kotlin/dto/MaintenanceDto.kt` · linhas 211–236 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/dto/MaintenanceDto.kt#L211-L236)

```kotlin
@Serializable
data class MaintenanceScheduleRequest(
    val equipmentId: String,
    val processId: String? = null,
    val recommendationId: String? = null,
    val title: String,
    val notes: String = "",
    val scheduledStart: String,
    val scheduledEnd: String? = null,
    val status: String = "planned",
)

@Serializable
data class MaintenanceScheduleResponse(
    val id: String,
    val equipmentId: String,
    val processId: String? = null,
    val recommendationId: String? = null,
    val title: String,
    val notes: String,
    val scheduledStart: String,
    val scheduledEnd: String? = null,
    val status: String,
    val createdAt: String,
    val updatedAt: String,
)
```

Fala: "Cada agenda pertence a um equipamento (`equipment_id`, obrigatório) e pode apontar para um processo (`process_id`, opcional), que é o CRUD do Alander. Se o processo for apagado, a agenda fica sem processo (`SET NULL`); se o equipamento for apagado, a agenda vai junto (`CASCADE`). As datas trafegam como texto ISO 8601."

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 405–405 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L405-L405)

```kotlin
    private fun schedule(r: ResultRow) = MaintenanceScheduleResponse(r[MaintenanceSchedulesTable.id].toString(), r[MaintenanceSchedulesTable.equipmentId].toString(), r[MaintenanceSchedulesTable.processId]?.toString(), r[MaintenanceSchedulesTable.recommendationId]?.toString(), r[MaintenanceSchedulesTable.title], r[MaintenanceSchedulesTable.notes], r[MaintenanceSchedulesTable.scheduledStart].iso(), r[MaintenanceSchedulesTable.scheduledEnd]?.iso(), r[MaintenanceSchedulesTable.status], r[MaintenanceSchedulesTable.createdAt].iso(), r[MaintenanceSchedulesTable.updatedAt].iso())
```

### 3.2 O que já existe

📍 `deviante-web/src/lib/api.js` · linhas 489–502 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/lib/api.js#L489-L502)

```javascript
  listSchedules: (params = {}) => {
    const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value != null && value !== '')).toString()
    return request(`/schedules${query ? `?${query}` : ''}`).then((payload) => {
      const rows = Array.isArray(payload) ? payload : payload?.items ?? []
      const normalized = rows.map((row) => ({
        ...row,
        scheduledStart: row.scheduledStart ?? row.plannedFor ?? null,
        scheduledEnd: row.scheduledEnd ?? null,
      }))
      return Array.isArray(payload) ? normalized : { ...payload, items: normalized }
    })
  },
  createSchedule: (data) => request('/schedules', { method: 'POST', body: JSON.stringify(data) }),
  updateSchedule: (id, patch) => request(`/schedules/${id}`, { method: 'PUT', body: JSON.stringify(patch) }),
```

Read (tela `/schedules`, lista, kanban e calendário):

📍 `deviante-web/src/pages/SchedulesPage.jsx` · linhas 11–17 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/203e38d/src/pages/SchedulesPage.jsx#L11-L17)

```jsx
export default function SchedulesPage() {
  const [rows, setRows] = useState([]); const [view, setView] = useState('list'); const [error, setError] = useState(''); const [loading, setLoading] = useState(true)
  const [searchParams] = useSearchParams()
  const equipmentId = searchParams.get('equipmentId')
  useEffect(() => { api.listSchedules({ equipmentId }).then((data) => setRows(Array.isArray(data) ? data : data?.items ?? [])).catch((err) => setError(err instanceof ApiError ? err.message : 'Não foi possível carregar os agendamentos.')).finally(() => setLoading(false)) }, [equipmentId])
  const actions = <div className="flex rounded-lg border border-border overflow-hidden">{VIEWS.map(({ id, label, icon: Icon }) => <button key={id} onClick={() => setView(id)} className="flex items-center gap-1.5 px-3 py-2 text-[11px]" style={{ border: 0, background: view === id ? 'var(--surface-inset)' : 'var(--surface-raised)', color: view === id ? 'var(--text-strong)' : 'var(--muted-foreground)' }}><Icon size={11} />{label}</button>)}</div>
  return <Surface title="Agendamentos" subtitle="Manutenções planejadas e ocorrências por equipamento." icon={Wrench} actions={actions}>{loading ? <State>Carregando…</State> : error ? <State error>{error}</State> : view === 'kanban' ? <Kanban rows={rows} /> : view === 'calendar' ? <Calendar rows={rows} /> : <ScheduleList rows={rows} />}</Surface>
```

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 764–769 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L764-L769)

```kotlin
                get {
                    val u=call.requireSupabaseUser(authClient)?:return@get
                    managerRepository.findOrCreateForSupabaseUser(u.id,u.email,u.fullNameHint)
                    val equipmentId = call.request.queryParameters["equipmentId"]?.let(::runCatchingUuid)
                    call.respond(maintenanceRepository.listSchedules(equipmentId))
                }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 345–353 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L345-L353)

```kotlin
    fun listSchedules(equipmentId: UUID? = null): List<MaintenanceScheduleResponse> = transaction {
        val query = MaintenanceSchedulesTable.selectAll()
        if (equipmentId != null) query.where { MaintenanceSchedulesTable.equipmentId eq equipmentId }
        query.orderBy(MaintenanceSchedulesTable.scheduledStart).map(::schedule)
    }

    fun findSchedule(id: UUID): MaintenanceScheduleResponse? = transaction {
        MaintenanceSchedulesTable.selectAll().where { MaintenanceSchedulesTable.id eq id }.firstOrNull()?.let(::schedule)
    }
```

Fala: "As três visões usam a mesma lista; só muda o agrupamento no front (por status no kanban, por mês no calendário). O filtro `?equipmentId=` vem da página do equipamento."

Create:

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 770–775 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L770-L775)

```kotlin
                post {
                    val u=call.requireSupabaseUser(authClient)?:return@post; val m=managerRepository.findOrCreateForSupabaseUser(u.id,u.email,u.fullNameHint); val body=call.receive<MaintenanceScheduleRequest>()
                    val start=runCatching{OffsetDateTime.parse(body.scheduledStart)}.getOrNull(); val end=body.scheduledEnd?.let{runCatching{OffsetDateTime.parse(it)}.getOrNull()}
                    if(body.title.isBlank()||start==null||(body.scheduledEnd!=null&&end==null)||(end!=null&&end<start)) { call.respond(HttpStatusCode.BadRequest,ErrorResponse("Agenda de manutenção inválida.")); return@post }
                    val item=runCatching{maintenanceRepository.createSchedule(m.id,body)}.getOrNull(); if(item==null) call.respond(HttpStatusCode.UnprocessableEntity,ErrorResponse("Referências da agenda inválidas.")) else call.respond(HttpStatusCode.Created,item)
                }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 355–367 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L355-L367)

```kotlin
    fun createSchedule(managerId: UUID, body: MaintenanceScheduleRequest): MaintenanceScheduleResponse? = transaction {
        val equipmentId = UUID.fromString(body.equipmentId)
        if (findEquipment(equipmentId) == null) return@transaction null
        val id = UUID.randomUUID(); val now = OffsetDateTime.now()
        MaintenanceSchedulesTable.insert {
            it[MaintenanceSchedulesTable.id] = id; it[MaintenanceSchedulesTable.equipmentId] = equipmentId
            it[MaintenanceSchedulesTable.processId] = body.processId?.let(UUID::fromString); it[MaintenanceSchedulesTable.recommendationId] = body.recommendationId?.let(UUID::fromString)
            it[MaintenanceSchedulesTable.managerId] = managerId; it[MaintenanceSchedulesTable.title] = body.title.trim(); it[MaintenanceSchedulesTable.notes] = body.notes.trim()
            it[MaintenanceSchedulesTable.scheduledStart] = OffsetDateTime.parse(body.scheduledStart); it[MaintenanceSchedulesTable.scheduledEnd] = body.scheduledEnd?.let(OffsetDateTime::parse)
            it[MaintenanceSchedulesTable.status] = body.status; it[MaintenanceSchedulesTable.createdAt] = now; it[MaintenanceSchedulesTable.updatedAt] = now
        }
        findSchedule(id)
    }
```

Fala: "A rota valida título, formato das datas e fim depois do início (400). O repositório confere se o equipamento existe; se não, devolve `null` e a rota responde 422."

Update e Delete:

📍 `deviante-api/src/main/kotlin/Routing.kt` · linhas 776–777 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/Routing.kt#L776-L777)

```kotlin
                put("/{id}") { call.requireSupabaseUser(authClient)?:return@put; val id=call.parameters["id"]?.let(::runCatchingUuid); val body=call.receive<MaintenanceScheduleRequest>(); val item=runCatching{id?.let{maintenanceRepository.updateSchedule(it,body)}}.getOrNull(); if(item==null) call.respond(HttpStatusCode.BadRequest,ErrorResponse("Agenda inválida ou não encontrada.")) else call.respond(item) }
                delete("/{id}") { call.requireSupabaseUser(authClient)?:return@delete; val id=call.parameters["id"]?.let(::runCatchingUuid); if(id==null||!maintenanceRepository.deleteSchedule(id)) call.respond(HttpStatusCode.NotFound,ErrorResponse("Agenda não encontrada.")) else call.respond(HttpStatusCode.NoContent) }
```

📍 `deviante-api/src/main/kotlin/repository/MaintenanceRepository.kt` · linhas 369–379 · [abrir no GitHub](https://github.com/aland3r/deviante-api/blob/1b5106c/src/main/kotlin/repository/MaintenanceRepository.kt#L369-L379)

```kotlin
    fun updateSchedule(id: UUID, body: MaintenanceScheduleRequest): MaintenanceScheduleResponse? = transaction {
        val changed = MaintenanceSchedulesTable.update({ MaintenanceSchedulesTable.id eq id }) {
            it[MaintenanceSchedulesTable.equipmentId] = UUID.fromString(body.equipmentId); it[MaintenanceSchedulesTable.processId] = body.processId?.let(UUID::fromString)
            it[MaintenanceSchedulesTable.recommendationId] = body.recommendationId?.let(UUID::fromString); it[MaintenanceSchedulesTable.title] = body.title.trim(); it[MaintenanceSchedulesTable.notes] = body.notes.trim()
            it[MaintenanceSchedulesTable.scheduledStart] = OffsetDateTime.parse(body.scheduledStart); it[MaintenanceSchedulesTable.scheduledEnd] = body.scheduledEnd?.let(OffsetDateTime::parse)
            it[MaintenanceSchedulesTable.status] = body.status; it[MaintenanceSchedulesTable.updatedAt] = OffsetDateTime.now()
        }
        if (changed == 0) null else findSchedule(id)
    }

    fun deleteSchedule(id: UUID): Boolean = transaction { MaintenanceSchedulesTable.deleteWhere { MaintenanceSchedulesTable.id eq id } > 0 }
```

### 3.3 A DESENVOLVER: validação no PUT

Hoje o `PUT` não valida datas nem título (só o `POST` valida). 📍 `deviante-api/src/main/kotlin/Routing.kt`, linha 776, trocar a rota por:

```kotlin
put("/{id}") {
    call.requireSupabaseUser(authClient) ?: return@put
    val id = call.parameters["id"]?.let(::runCatchingUuid)
    val body = call.receive<MaintenanceScheduleRequest>()
    val start = runCatching { OffsetDateTime.parse(body.scheduledStart) }.getOrNull()
    val end = body.scheduledEnd?.let { runCatching { OffsetDateTime.parse(it) }.getOrNull() }
    if (id == null || body.title.isBlank() || start == null || (body.scheduledEnd != null && end == null) || (end != null && end < start)) {
        call.respond(HttpStatusCode.BadRequest, ErrorResponse("Agenda de manutenção inválida."))
        return@put
    }
    val item = runCatching { maintenanceRepository.updateSchedule(id, body) }.getOrNull()
    if (item == null) call.respond(HttpStatusCode.NotFound, ErrorResponse("Agenda não encontrada.")) else call.respond(item)
}
```

### 3.4 A DESENVOLVER: criar, editar e excluir na tela `/schedules`

📍 `deviante-web/src/lib/api.js`, depois de `updateSchedule` (linha 502):

```javascript
  deleteSchedule: (id) => request(`/schedules/${id}`, { method: 'DELETE' }),
```

📍 `deviante-web/src/pages/SchedulesPage.jsx`: na linha 12, novo estado `const [editing, setEditing] = useState(null)`; na linha 14, transformar a busca numa função `load` para recarregar depois de salvar; na linha 15, um botão "Nova manutenção" ao lado das visões; e o `Card` (linha 19) recebe `onClick={() => setEditing(row)}`. O modal novo, no fim do arquivo:

```jsx
function ScheduleModal({ initial, onClose, onSaved }) {
  const [machines, setMachines] = useState([])
  const [processes, setProcesses] = useState([])
  const [values, setValues] = useState({
    title: initial?.title ?? '', equipmentId: initial?.equipmentId ?? '', processId: initial?.processId ?? '',
    scheduledStart: initial?.scheduledStart?.slice(0, 16) ?? '', scheduledEnd: initial?.scheduledEnd?.slice(0, 16) ?? '',
    status: initial?.status ?? 'planned', notes: initial?.notes ?? '',
  })
  const [error, setError] = useState('')
  useEffect(() => { api.listAllMachines().then(setMachines); api.listProcesses().then(setProcesses) }, [])
  const set = (key) => (event) => setValues((current) => ({ ...current, [key]: event.target.value }))
  const iso = (local) => (local ? new Date(local).toISOString() : null)

  async function save(event) {
    event.preventDefault()
    const body = { ...values, processId: values.processId || null, scheduledStart: iso(values.scheduledStart), scheduledEnd: iso(values.scheduledEnd) }
    try {
      if (initial?.id) await api.updateSchedule(initial.id, body)   // Update
      else await api.createSchedule(body)                          // Create
      onSaved()
    } catch (err) { setError(err instanceof ApiError ? err.message : 'Não foi possível salvar.') }
  }
  async function remove() {                                         // Delete
    if (!window.confirm('Excluir esta manutenção?')) return
    await api.deleteSchedule(initial.id); onSaved()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(3,6,12,.78)' }}>
      <form onSubmit={save} className="w-full rounded-xl border border-border p-4 grid gap-3" style={{ maxWidth: 480, background: 'var(--surface-raised)' }}>
        <h2 className="text-sm font-semibold">{initial?.id ? 'Editar manutenção' : 'Nova manutenção'}</h2>
        <input required value={values.title} onChange={set('title')} placeholder="Título" />
        <select required value={values.equipmentId} onChange={set('equipmentId')}>
          <option value="">Equipamento *</option>
          {machines.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
        </select>
        <select value={values.processId} onChange={set('processId')}>
          <option value="">Sem processo</option>
          {processes.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <label>Início <input required type="datetime-local" value={values.scheduledStart} onChange={set('scheduledStart')} /></label>
        <label>Fim <input type="datetime-local" value={values.scheduledEnd} onChange={set('scheduledEnd')} /></label>
        <select value={values.status} onChange={set('status')}>{Object.entries(STATUS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
        <textarea value={values.notes} onChange={set('notes')} placeholder="Observações" />
        {error && <State error>{error}</State>}
        <div className="flex justify-between">
          {initial?.id ? <button type="button" onClick={remove}>Excluir</button> : <span />}
          <span><button type="button" onClick={onClose}>Cancelar</button> <button>Salvar</button></span>
        </div>
      </form>
    </div>
  )
}
```

Fala sobre o modal: "o mesmo formulário faz Create e Update; o select de equipamento vem do CRUD de Equipamento e o de processo vem do CRUD de Processo, que é a relação entre as tabelas aparecendo na tela."

### 3.5 Roteiro de fala

1. Abrir `https://deviante.alander.io/schedules`. Clicar "Nova manutenção": "Troca de rolamento", Torno CNC Prod1, um processo, início amanhã (Create: `POST /api/schedules`, 201).
2. Mostrar as três visões (lista, kanban, calendário): mesma API, agrupamentos diferentes.
3. Abrir o card, mudar o status para "Em andamento" e salvar (Update: `PUT /api/schedules/{id}`). O card muda de coluna no kanban.
4. Tentar salvar com fim antes do início: 400. Explicar o 422 quando o equipamento não existe.
5. Excluir a manutenção (Delete: 204).
6. Fechar: "no meu par de CRUDs são duas tabelas, `equipment` e `maintenance_schedules`, ligadas por FK; a agenda ainda aponta para `processes`, que é o CRUD do Alander".

## 4. Perguntas prováveis

- **Por que um repositório só para equipamento e agenda?** Os dois são do mesmo contexto (manutenção) e a agenda reaproveita `findEquipment` para validar a FK antes do insert.
- **O que acontece ao excluir um equipamento que tem agenda?** O banco apaga a agenda junto (`ON DELETE CASCADE` em `maintenance_schedules.equipment_id`).
- **Onde fica a transação?** Cada função do repositório roda em `transaction { }` do Exposed, com conexão do pool aberto em `Database.kt`.
- **Por que datas como texto no JSON?** O corpo traz ISO 8601; o Core converte com `OffsetDateTime.parse` e responde 400 se o formato for inválido.

## 5. Checagem antes de ensaiar

- [ ] Editar e excluir em `EquipmentPage.jsx` publicados.
- [ ] `ScheduleModal`, botão "Nova manutenção" e `api.deleteSchedule` publicados.
- [ ] Validação no `PUT /api/schedules/{id}` publicada.
- [ ] Trocar os blocos A DESENVOLVER pelos links reais depois do commit.
