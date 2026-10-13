# Reuso 03, item 03: roteiro do vídeo de compactação de código por reuso

O enunciado pede o repositório e uma técnica de compactação de código focada em reuso, demonstrada passo a passo num vídeo não listado no YouTube (um por equipe). Este é o roteiro do vídeo: o que mostrar, em que ordem e o que falar. Duração alvo: 4 a 5 minutos.

## A técnica

**Extração de componente reutilizável por composição.** Os três formulários em modal do sistema (Equipamento, Agenda de manutenção e Atividade) repetiam o mesmo esqueleto: fundo escuro, cartão, cabeçalho com título e botão de fechar, grade de campos, mensagem de erro, rodapé com Cancelar e Salvar, e as mesmas classes em cada `input`, `select` e `textarea`. A técnica tira esse esqueleto para um componente só, `FormModal`, mais quatro peças de campo (`Field`, `TextInput`, `Select`, `TextArea`). Cada tela passa a declarar apenas o que é dela: os campos e a ação de salvar. O conteúdo variável entra por `children` e por propriedades (`title`, `canSubmit`, `footerStart`, `columns`).

O antes e o depois estão em dois commits seguidos do `deviante-web`, o que deixa o vídeo reproduzível:

| | Commit |
|---|---|
| Antes | `5c86907` (Telas de CRUD e Observer) |
| Depois | `7ddb9a0` (Compactação por reuso: FormModal compartilhado) |

Números medidos nos três modais:

| Modal | Antes (caracteres) | Depois (caracteres) |
|---|---|---|
| `CreateEquipmentModal` | 3.199 | 1.873 |
| `ScheduleModal` | 4.562 | 2.859 |
| `ActivityModal` | 4.534 | 3.162 |
| **Total dos modais** | **12.295** | **7.894 (−36%)** |
| `FormModal.jsx` (novo, escrito uma vez) | | 2.826 |

Mesmo contando o componente novo, o total cai de 12.295 para 10.720 caracteres. O ganho cresce a cada formulário novo, que passa a custar só os campos.

## O componente

📍 `deviante-web/src/components/ui/FormModal.jsx` · linhas 1–56 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/fa44226/src/components/ui/FormModal.jsx#L1-L56)

```jsx
import { X } from 'lucide-react'

/*
  Moldura reutilizável dos formulários em modal (Equipamento, Agenda e
  Atividade). Antes cada tela repetia o fundo escuro, o cabeçalho com fechar,
  o rodapé com Cancelar/Salvar e as classes de cada campo; agora só declara os
  campos. É a técnica de compactação por reuso da entrega Reuso 03 (item 03).
*/
const inputClass = 'px-3 py-2 rounded-lg border border-border text-xs text-foreground'
const inputStyle = { background: 'var(--surface-base)' }

export function Field({ label, wide = false, children }) {
  return <label className={`flex flex-col gap-1 text-[10px] text-muted-foreground ${wide ? 'sm:col-span-2' : ''}`}>{label}{children}</label>
}

export function TextInput(props) {
  return <input {...props} className={inputClass} style={inputStyle} />
}

export function Select({ children, ...props }) {
  return <select {...props} className={inputClass} style={inputStyle}>{children}</select>
}

export function TextArea(props) {
  return <textarea rows={3} {...props} className={inputClass} style={inputStyle} />
}

export default function FormModal({
  title, subtitle, onClose, onSubmit, busy = false, canSubmit = true,
  submitLabel = 'Salvar', error = '', footerStart = null, columns = 2, children,
}) {
  const submit = (event) => { event.preventDefault(); if (canSubmit && !busy) onSubmit() }
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(3,6,12,.78)' }}>
      <form onSubmit={submit} className="w-full rounded-xl border border-border" style={{ maxWidth: 480, background: 'var(--surface-raised)' }}>
        <div className="flex justify-between px-4 py-3 border-b border-border">
          <div>
            <h2 className="text-sm font-semibold text-foreground">{title}</h2>
            {subtitle && <p className="text-[11px] text-muted-foreground mt-1">{subtitle}</p>}
          </div>
          <button type="button" onClick={onClose} aria-label="Fechar"><X size={13} /></button>
        </div>
        <div className={`grid gap-3 p-4 ${columns === 2 ? 'sm:grid-cols-2' : ''}`}>
          {children}
          {error && <p className={`text-[11px] ${columns === 2 ? 'sm:col-span-2' : ''}`} style={{ color: 'var(--crit-soft)' }}>{error}</p>}
        </div>
        <div className="flex items-center gap-2 px-4 py-3 border-t border-border">
          {footerStart}
          <div className="flex-1" />
          <button type="button" onClick={onClose} className="px-3 py-2 text-xs text-muted-foreground">Cancelar</button>
          <button disabled={busy || !canSubmit} className="px-3 py-2 rounded-lg text-xs font-semibold text-white disabled:opacity-50" style={{ background: 'var(--ok-strong)' }}>{busy ? 'Salvando…' : submitLabel}</button>
        </div>
      </form>
    </div>
  )
}
```

## Antes e depois de um uso

Depois (Agenda de manutenção):

📍 `deviante-web/src/pages/SchedulesPage.jsx` · linhas 65–89 · [abrir no GitHub](https://github.com/aland3r/deviante-web/blob/fa44226/src/pages/SchedulesPage.jsx#L65-L89)

```jsx
function ScheduleModal({ initial, onClose, onSave, onDelete }) {
  const [equipment, setEquipment] = useState([])
  const [values, setValues] = useState({
    equipmentId: initial.equipmentId ?? '', title: initial.title ?? '', notes: initial.notes ?? '',
    scheduledStart: toLocalInput(initial.scheduledStart), scheduledEnd: toLocalInput(initial.scheduledEnd), status: initial.status ?? 'planned',
  })
  const [busy, setBusy] = useState(false); const [error, setError] = useState('')
  useEffect(() => { api.listAllMachines().then((data) => setEquipment(Array.isArray(data) ? data : data?.items ?? [])).catch(() => setEquipment([])) }, [])
  const set = (key) => (event) => setValues((current) => ({ ...current, [key]: event.target.value }))
  const valid = Boolean(values.equipmentId && values.title.trim() && values.scheduledStart && (!values.scheduledEnd || values.scheduledEnd >= values.scheduledStart))
  const run = async (action) => { setBusy(true); setError(''); try { await action() } catch (err) { setError(err instanceof ApiError ? err.message : 'Não foi possível salvar a manutenção.') } finally { setBusy(false) } }
  const submit = () => run(() => onSave({
    equipmentId: values.equipmentId, processId: initial.processId ?? null, recommendationId: initial.recommendationId ?? null,
    title: values.title.trim(), notes: values.notes.trim(), scheduledStart: toIso(values.scheduledStart), scheduledEnd: toIso(values.scheduledEnd), status: values.status,
  }))
  const remove = onDelete && <button type="button" disabled={busy} onClick={() => run(onDelete)} className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs" style={{ color: 'var(--crit-soft)' }}><Trash2 size={12} />Excluir</button>
  return <FormModal title={initial.id ? 'Editar manutenção' : 'Nova manutenção'} onClose={onClose} onSubmit={submit} busy={busy} canSubmit={valid} error={error} footerStart={remove}>
    <Field label="Título *" wide><TextInput value={values.title} onChange={set('title')} placeholder="Ex.: Troca de rolamentos" /></Field>
    <Field label="Equipamento *" wide><Select value={values.equipmentId} onChange={set('equipmentId')}><option value="">Selecione…</option>{equipment.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</Select></Field>
    <Field label="Início *"><TextInput type="datetime-local" value={values.scheduledStart} onChange={set('scheduledStart')} /></Field>
    <Field label="Fim"><TextInput type="datetime-local" value={values.scheduledEnd} onChange={set('scheduledEnd')} /></Field>
    <Field label="Situação"><Select value={values.status} onChange={set('status')}>{Object.entries(STATUS).map(([value, text]) => <option key={value} value={value}>{text}</option>)}</Select></Field>
    <Field label="Observações" wide><TextArea value={values.notes} onChange={set('notes')} /></Field>
  </FormModal>
}
```

## Roteiro de gravação

Preparar antes: VS Code aberto no `deviante-web`, terminal na raiz, o site aberto em `https://deviante.alander.io` com a conta **Gestor**.

1. **Abertura (20 s).** Tela do site. Fala: "Este é o Deviante. Vamos mostrar uma técnica de compactação de código focada em reuso: extrair um componente reutilizável para eliminar código repetido entre telas."
2. **O problema (60 s).** No terminal: `git checkout 5c86907`. Abrir lado a lado `src/pages/EquipmentPage.jsx` (função `CreateEquipmentModal`), `src/pages/SchedulesPage.jsx` (`ScheduleModal`) e `src/pages/ActivitiesPage.jsx` (`ActivityModal`). Selecionar em cada um o `div` de fundo, o cabeçalho com o `X`, o rodapé com Cancelar/Salvar e as classes repetidas dos campos. Fala: "três telas, o mesmo esqueleto copiado três vezes; uma mudança de estilo hoje precisa ser feita em três lugares".
3. **A extração (60 s).** `git checkout 7ddb9a0`. Abrir `src/components/ui/FormModal.jsx`. Mostrar o esqueleto que saiu das telas, as peças de campo e as propriedades que variam: `title`, `canSubmit`, `error`, `footerStart` (o botão Excluir da Agenda) e `columns` (a Atividade usa uma coluna). Fala: "o que é igual fica aqui; o que muda entra por `children` e por propriedades".
4. **O uso (60 s).** Abrir de novo `ScheduleModal` e `ActivityModal`. Mostrar que cada um agora é só lógica e campos. Rodar `git show --stat 7ddb9a0` e mostrar a tabela de números acima. Fala: "os modais caíram 36%; um formulário novo custa só os campos".
5. **Funciona igual (45 s).** No site, abrir **Equipamentos → Novo equipamento**, **Agendamentos → Nova manutenção** (mostrar o Excluir ao editar) e **Atividades → Nova atividade**. Fala: "a aparência e o comportamento não mudaram; mudou só quanto código cada tela carrega".
6. **Fechamento (20 s).** Fala: "a técnica é a mesma que usamos no back-end com o `AppConfig` e os adaptadores: escrever uma vez e reaproveitar. O repositório está em github.com/aland3r/deviante-web."

Publicar no YouTube como **Não listado** e colar o link na entrega junto com os repositórios (`aland3r/deviante-web`, `aland3r/deviante-api`, `aland3r/deviante-docs`).
