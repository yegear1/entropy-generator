# 🔐 YeHub Entropy Generator

Gerador de senhas e passphrases com alta entropia, construído com **FastAPI** (backend) e **HTML/JS** (frontend).

---

## 📁 Estrutura do Projeto

```
entropy-generator/
├── backend/
│   ├── app/
│   │   ├── main.py              # Entry point — FastAPI app, CORS e servir frontend
│   │   ├── config/
│   │   │   └── logger.py        # Configuração do Loguru (stdout + arquivo)
│   │   ├── routers/
│   │   │   └── generator.py     # Rotas da API (/api/v1/generate/*)
│   │   └── services/
│   │       └── entropy_generator.py  # Lógica de geração (password + passphrase)
│   ├── data/
│   │   ├── english_wordlist.txt     # Wordlist em inglês para passphrases
│   │   └── portuguese.wordlist.txt  # Wordlist em português para passphrases
│   └── requirements.txt
├── frontend/
│   └── index.html               # Interface completa (HTML + CSS + JS)
└── .venv/                       # Ambiente virtual Python
```

---

## 🔗 Como o Backend e o Frontend se conectam

A integração acontece em **3 camadas**:

### 1. Frontend faz requisições HTTP para a API

No `frontend/index.html`, o JavaScript define a URL base da API e faz `fetch()` para os endpoints:

```javascript
const API_BASE = 'http://localhost:8000/api/v1/generate';

// Geração de senha
const params = new URLSearchParams({
    length: 24,
    use_upper: true,
    use_lower: true,
    use_digits: true,
    use_specials: true,
    use_emojis: false
});
const response = await fetch(`${API_BASE}/password?${params.toString()}`);
const data = await response.json();
console.log(data.password); // => "uPp_Thoi9fon;>C."

// Geração de passphrase
const response = await fetch(`${API_BASE}/passphrase?words=6&language=en`);
const data = await response.json();
console.log(data.passphrase); // => "correct-horse-battery-staple-cyber-vault"
```

### 2. Backend expõe as rotas da API via FastAPI Router

No `backend/app/routers/generator.py`, as rotas são definidas com um `APIRouter` e prefixo `/api/v1/generate`:

```python
router = APIRouter(prefix="/api/v1/generate", tags=["Generator"])

@router.get("/password")
async def get_generated_password(length: int = 24, ...):
    senha = generate_password(length, ...)
    return {"password": senha}

@router.get("/passphrase")
async def get_generated_passphrase(words: int = 6, language: str = "pt"):
    frase = generate_passphrase(words, language=language)
    return {"passphrase": frase}
```

O router é registrado no `main.py`:

```python
from app.routers import generator
app.include_router(generator.router)
```

### 3. CORS permite que o frontend acesse a API

Sem CORS, o navegador **bloquearia** as requisições do frontend para o backend (por serem origens diferentes). A configuração no `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Em produção, restrinja para seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Frontend servido pelo próprio FastAPI (opcional)

Para conveniência, o backend também serve o frontend como arquivo estático. Ao acessar `http://localhost:8000/`, o FastAPI entrega o `index.html`:

```python
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))
```

> **Nota:** O frontend também possui um **fallback local** — se o backend estiver offline, ele gera senhas/passphrases diretamente no navegador usando `crypto.getRandomValues()`.

---

## 🔄 Fluxo Completo de uma Requisição

```
┌──────────────┐     GET /api/v1/generate/password?length=24     ┌──────────────┐
│              │ ──────────────────────────────────────────────►  │              │
│   Frontend   │                                                  │   Backend    │
│  (index.html)│  ◄──────────────────────────────────────────────  │  (FastAPI)   │
│              │     { "password": "aX9#kL...mZ" }                │              │
└──────────────┘                                                  └──────┬───────┘
                                                                         │
                                                                         ▼
                                                                  ┌──────────────┐
                                                                  │   Services   │
                                                                  │  (entropy_   │
                                                                  │  generator)  │
                                                                  └──────────────┘
```

---

## 🚀 Como Rodar

### Pré-requisitos

- Python 3.10+
- pip

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r backend/requirements.txt
```

### 3. Iniciar o servidor

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Acessar

| URL | Descrição |
|-----|-----------|
| `http://localhost:8000` | Interface do frontend |
| `http://localhost:8000/docs` | Swagger UI (documentação interativa da API) |
| `http://localhost:8000/redoc` | ReDoc (documentação alternativa) |
| `http://localhost:8000/health` | Health check |

---

## 📡 Endpoints da API

### `GET /api/v1/generate/password`

Gera uma senha aleatória com alta entropia.

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `length` | `int` | `24` | Comprimento da senha (9–128) |
| `use_upper` | `bool` | `true` | Incluir letras maiúsculas (A-Z) |
| `use_lower` | `bool` | `true` | Incluir letras minúsculas (a-z) |
| `use_digits` | `bool` | `true` | Incluir dígitos (0-9) |
| `use_specials` | `bool` | `true` | Incluir símbolos (!@#$%...) |
| `use_emojis` | `bool` | `false` | Incluir emojis (🚀👽🔥) |

**Exemplo:**

```bash
curl "http://localhost:8000/api/v1/generate/password?length=16&use_emojis=true"
```

```json
{ "password": "aX9🔥#kL2mZ!rT🚀w" }
```

---

### `GET /api/v1/generate/passphrase`

Gera uma passphrase (frase-senha) com palavras aleatórias de uma wordlist.

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `words` | `int` | `6` | Quantidade de palavras (5–12) |
| `language` | `str` | `"pt"` | Idioma da wordlist (`"en"` ou `"pt"`) |

**Exemplo:**

```bash
curl "http://localhost:8000/api/v1/generate/passphrase?words=5&language=en"
```

```json
{ "passphrase": "correct-horse-battery-staple-cipher" }
```

---

### `GET /health`

Verifica se a API está online.

```json
{ "status": "online", "message": "YeHub API is running" }
```

---

## 🛡️ Segurança

- Usa o módulo `secrets` do Python (CSPRNG) para geração criptograficamente segura
- Garante pelo menos **1 caractere de cada tipo selecionado** na senha
- Resultado final é embaralhado com `secrets.SystemRandom().shuffle()`
- Frontend usa `crypto.getRandomValues()` no fallback (também CSPRNG)

---

## 📝 Licença

MIT
