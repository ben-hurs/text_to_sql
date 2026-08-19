# Text-to-SQL - Perguntas em Linguagem Natural

Uma API REST construída com **FastAPI**, **PostgreSQL** e a **API da Anthropic (Claude)** que converte perguntas em linguagem natural (português) em queries SQL válidas, executa no banco de dados e retorna o resultado. Este projeto foi desenvolvido como aprendizado prático de integração entre LLMs e bancos de dados relacionais.

---

## Sobre o Projeto

Este projeto tem dependência de **dados**, se conecta ao mesmo banco `clientes_db`, criado e populado pelo `init_db.py` do [postgres_fastapi](https://github.com/ben-hurs/postgres_fastapi).

O que aprendi:

- Integrar a API da Anthropic (Claude) em uma aplicação Python
- Técnica de Text-to-SQL: traduzir linguagem natural para SQL usando um LLM
- Separar `system prompt` (contexto fixo) de `user prompt` (o que muda a cada chamada)
- Validar e sanitizar SQL gerado por IA antes de executar no banco (segurança contra queries destrutivas)
- Executar SQL "cru" no SQLAlchemy usando `text()`
- Usar variáveis de ambiente (`.env`) para não expor credenciais no código
- Debugar respostas de API inspecionando o objeto de resposta completo, não só o campo esperado

---

## Estrutura do Projeto

```
text_to_sql/
├── src/
│   ├── __init__.py
│   ├── database.py       
│   ├── models.py         
│   ├── schemas.py        
│   ├── nl_sql_engine.py  
│   └── api.py            
├── main.py               
├── requirements.txt     
├── .env                  
└── .gitignore
```

---

## Como Funciona

### O Fluxo Completo

```
"Quantos clientes eu tenho?"
        ↓
[Claude recebe o schema da tabela + a pergunta]
        ↓
"SELECT COUNT(*) FROM clientes;"
        ↓
[Validação: é um SELECT? Sim → segue. Não → bloqueia]
        ↓
[Executa no PostgreSQL]
        ↓
{"count": 4}
```

### Geração do SQL

O `nl_sql_engine.py` envia para o Claude um `system prompt` fixo contendo o schema da tabela `clientes` (colunas e tipos) e as regras de formato de resposta, junto com a pergunta do usuário. O modelo retorna apenas a query SQL, sem explicações ou markdown.

### Validação de Segurança

Antes de qualquer execução no banco, o SQL gerado passa por uma validação: só queries que começam com `SELECT` são executadas. Isso protege contra o LLM gerar (por erro ou manipulação da pergunta) comandos destrutivos como `DELETE` ou `DROP`, mesmo que o prompt já instrua o modelo a nunca gerar isso, essa é uma segunda camada de proteção no próprio código, que não depende do LLM se comportar corretamente.

### Execução e Resposta

Se a validação passar, a query roda via `db.execute(text(sql))`. As colunas e linhas retornadas são combinadas em uma lista de dicionários e devolvidas junto com a pergunta original, o SQL gerado e a contagem de registros, dando transparência total sobre o que a IA gerou e executou.

---

## Instalação e Uso

### Pré-requisitos

- Python 3.10+
- PostgreSQL rodando com o banco `clientes_db` já criado (via projeto 1)
- Uma chave de API da Anthropic ([console.anthropic.com](https://console.anthropic.com))

### 1. Clone o repositório

```bash
git clone https://github.com/ben-hurs/text_to_sql
cd text_to_sql
```

### 2. Crie e ative o ambiente virtual

```bash
# Linux/Mac/WSL
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```
DATABASE_URL=postgresql+psycopg2://postgres:senha123@localhost:5432/clientes_db
ANTHROPIC_API_KEY=sua_chave_aqui
```

> O banco `clientes_db` precisa já existir e estar populado, rode o `init_db.py` do [projeto 1](https://github.com/ben-hurs/postgres_fastapi) antes, caso ainda não tenha feito.

### 5. Rode a aplicação

```bash
python main.py
```

A API estará disponível em: <http://localhost:8000>

---

## Testando a API

### Com Swagger UI

Abra no navegador: <http://localhost:8000/docs>

### Com cURL

```bash
curl -X POST http://localhost:8000/ask-natural-language \
  -H "Content-Type: application/json" \
  -d '{"pergunta":"quantos clientes eu tenho?"}'
```

### Exemplos de Perguntas Testadas

**Pergunta:** "quantos clientes eu tenho?"
```json
{
  "pergunta": "quantos clientes eu tenho?",
  "sql_gerado": "SELECT COUNT(*) FROM clientes;",
  "resultados": [{"count": 4}],
  "total_registros": 1
}
```

**Pergunta:** "me mostra o nome e email de todos os clientes"
```json
{
  "pergunta": "me mostra o nome e email de todos os clientes",
  "sql_gerado": "SELECT nome, email FROM clientes;",
  "resultados": [
    {"nome": "Alice Silva", "email": "alice@example.com"},
    {"nome": "Bob Santos", "email": "bob@example.com"}
  ],
  "total_registros": 2
}
```

**Pergunta:** "qual cliente tem o email mais recente cadastrado?"

Como a tabela não possui coluna de data, o modelo improvisou usando o `id` como proxy de ordem de cadastro:
```json
{
  "sql_gerado": "SELECT * FROM clientes ORDER BY id DESC LIMIT 1;"
}
```

---

## Dificuldades Encontradas

### Variável de Ambiente Não Carregada

Um dos módulos (`nl_sql_engine.py`) usava `os.getenv()` sem antes chamar `load_dotenv()` nesse mesmo arquivo, o `.env` só era carregado quando `database.py` era importado primeiro. A lição: cada módulo que depende de variáveis de ambiente deve garantir seu próprio carregamento, sem depender da ordem de import de outros arquivos.

---

## Referências Úteis

- Anthropic API Documentation: <https://docs.claude.com>
- FastAPI Documentation: <https://fastapi.tiangolo.com/>
- SQLAlchemy Core (raw SQL com `text()`): <https://docs.sqlalchemy.org/en/20/core/>
- Pydantic Validation: <https://docs.pydantic.dev/>