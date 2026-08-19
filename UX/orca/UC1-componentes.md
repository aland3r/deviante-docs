# UC1 — Componentes (Manter conta de usuário)

Caso de uso: [[../user stories/ABP-DV-UC1-MaintainUserAccount|ABP-DV-UC1]]  
ORCA: [[S6 Notion ORCA Hub|Notion ORCA Hub]] (objeto **User**, CTAs de login/registro)

## Onde alterar e estilizar

| Camada | Onde | O que muda |
|--------|------|------------|
| **Estrutura (sem estilo produto)** | Figma **Alander Design System** → `library` | Variant sets, anatomia, tokens alto nível |
| **Estilo Deviante** | Figma Deviante → páginas **`styles`** | Tema produto (accent, auth grayscale…) |
| **Componentes estilizados** | Figma Deviante → **`library`** (`142:896`) | Instâncias ADS + overrides de estilo |
| **Protótipo UC** | Figma Deviante → **`use cases`** | **Só frames de tela** — filhos = instâncias da library Deviante |
| **Código** | `deviante/web/src/components/ui/` + `index.css` | Implementação React |
| **Tokens código** | `tokens/` | Espelho variables |

**Regra absoluta:** em `use cases`, nada sem link Deviante library → ADS. Ver skill [[../../../../doc/agents/deviante-figma-use-cases|deviante-figma-use-cases]].

Links: [[S4 Alander Design System ADS|S4 ADS]] · [[S5 Deviante Figma v1.0|S5 Deviante]] · [[../../../../design-system/README|design-system]]

---

## Inventário de componentes

### Feito no ADS — `library` → seção **UC1 · Components** ✓

Component sets publicados (2026-07-14): Button/Primary, Button/Ghost, Button/Social, Input/Text, Input/Email, Input/Password, Alert/Inline, Link/Text, Divider/Text, Text/Legal, Auth/BrandMark, Auth/EmailSummary, Auth/SplitLayout, Card/Form, App/Header.

| Component set | Variantes | Mapeia React | UC1 |
|---------------|-----------|--------------|-----|
| **Button/Primary** | size: sm/md/lg · state: default/hover/disabled/loading | `Button.jsx` variant primary | Login continuar, Entrar, Cadastrar, Salvar |
| **Button/Secondary** | idem | `Button.jsx` secondary | — |
| **Button/Ghost** | idem | `Button.jsx` ghost | Alterar e-mail |
| **Button/Social** | provider: google · state: default/disabled/loading | `SocialLoginButton.jsx` | Continuar com Google (v1.0) |
| **Input/Text** | state: default/focus/error/disabled | `FormField.jsx` | Nome, based in; empresa (processo) |
| **Input/Select** | — | `select.form-field__input` | Idioma principal, idioma de interface |
| **Input/Email** | state + withIcon: true/false | `LoginPage` auth-email-field | Login passo 1 |
| **Input/Password** | state | `FormField.jsx` type password | Login passo 2, registro, settings |
| **Alert/Inline** | intent: error/success | `Alert.jsx` | Erros de validação, sucesso settings |
| **Link/Text** | size: sm/md | `<Link>`, `.auth-split__footer` | Criar conta, Entrar, Termos |
| **Divider/Text** | — | `.auth-split__divider` | "Ou informe seu e-mail…" |
| **Text/Legal** | — | `.auth-split__legal` | Termos de uso |
| **Auth/BrandMark** | size: sm/lg | `.auth-split__brand`, `.brand-mark` | Logo DV |
| **Auth/EmailSummary** | — | `.auth-split__email-summary` | Login passo 2 (e-mail + Alterar) |
| **Auth/SplitLayout** | — (template) | `AuthSplitLayout.jsx` | Login |
| **Auth/HeroPanel** | — | `.auth-split__hero` | Painel direito login |
| **Card/Form** | — | `.card`, `.auth-layout__card` | Registro, settings |
| **App/Header** | auth: true/false | `AppLayout.jsx` | Settings (autenticado) |

### Telas no Deviante v1.0 — página **`use cases`**

| Frame | Rota | Passos UC1 |
|-------|------|------------|
| `UC1 · Login · Email` | `/login` step 1 | Google + e-mail + Continuar |
| `UC1 · Login · Password` | `/login` step 2 | Resumo e-mail + senha + Entrar |
| `UC1 · Register` | `/register` | Formulário completo + Cadastrar |
| `UC1 · Complete Profile` | `/register/complete` (pós-OAuth) | Idiomas + localização opcional + Concluir cadastro |
| `UC1 · Account Settings` | `/account` | App shell + form + Salvar alterações |

Estados por tela: **default**, **validation error** (2.1 / 2a.1 / 2b.1), **loading**, **success** (2c).

**Figma:** https://www.figma.com/design/DzMGsKozRhijjcFFngdy4S/--PIBITI-----Deviante-v1.0 — página `use cases`

---

## Campos do UC1 (referência)

| Campo | Register | Complete Profile | Settings | Process (UC2) | Validação |
|-------|----------|------------------|----------|---------------|-----------|
| Nome completo | ✓ | — (Google) | ✓ | — | obrigatório |
| E-mail | ✓ | — (Google) | ✓ | — | único (AC2) |
| Senha | ✓ | — | opcional | — | AC1 |
| Idioma principal | ✓ | ✓ | ✓ | — | obrigatório (AC8) |
| Idioma de interface | ✓ | ✓ | ✓ | — | obrigatório; ≠ principal (AC8) |
| Exibir localização | ✓ | ✓ | ✓ | — | opcional (AC9) |
| Based in | se toggle | se toggle | se toggle | — | obrigatório se toggle (AC9) |
| Empresa | — | — | — | ✓ | UC2-AC4 |

---

## CTAs (labels exatas — ORCA / código)

| CTA | Onde |
|-----|------|
| Continuar com Google | Login email step |
| Criar conta | Login footer → `/register` |
| Continuar | Login email step |
| Entrar | Login password step |
| Cadastrar | Register submit |
| Concluir cadastro | Complete profile (pós-OAuth) |
| Salvar alterações | Account settings |
| Sair | App header (autenticado) |
| Alterar | Trocar e-mail no login |

---

## Prompt pendente — agente Figma (**Deviante · use cases**)

Regra: skill **deviante-figma-use-cases** — só frames de tela; instâncias da **library Deviante** (nunca ADS direto; nunca elemento solto).

```
Arquivo: PIBITI Deviante v1.0 (fileKey DzMGsKozRhijjcFFngdy4S)
Página: use cases

PRÉ-REQUISITO: componentes já estilizados na library Deviante (142:896), com link ADS. Estilo aplicado nas páginas styles do Deviante — NÃO nesta página.

Criar seção "UC1 · Maintain User Account" com 5 FRAMES 1440×900 (nada mais na página além dos frames):

1. UC1 · Login · Email
2. UC1 · Login · Password
3. UC1 · Register
4. UC1 · Complete Profile
5. UC1 · Account Settings

Dentro de cada frame: SOMENTE instâncias da library Deviante (Button/Primary, Auth/SplitLayout, Input/Email, etc.). Trocar variantes e textos PT; zero texto solto, zero retângulo local, zero instância direta do ADS. Apenas **Continuar com Google** — sem outros providers.

Conteúdo por frame — ver tabela CTAs e inventário acima. Prototype links entre os 5 frames.

Auditoria final: cada nó filho do frame = INSTANCE → mainComponent na library Deviante → link ADS.
```

---

## Bloqueio MCP (Cursor)

Para o Cursor criar direto no Figma via MCP, compartilhe **Alander Design System** e **Deviante v1.0** (node `142:896`) com permissão de **editor**. O MCP pode atingir limite de chamadas no plano View — use o agente nativo do Figma se necessário.

Até lá: use o prompt pendente acima no **agente nativo do Figma**.

> Quando executar um prompt, avise no chat — removemos o bloco e marcamos ✓ no inventário.
