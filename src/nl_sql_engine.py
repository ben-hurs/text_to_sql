from anthropic import Anthropic

from sqlalchemy import text
from sqlalchemy.orm import Session

from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """Você é um especialista em SQL que traduz perguntas em linguagem natural para queries SQL válidas no PostgreSQL.

Schema do banco de dados:

Tabela: clientes
Colunas:
- id (integer, chave primária)
- nome (texto)
- email (texto, único)

Regras:
- Responda APENAS com a query SQL, nada mais
- Não inclua explicações, comentários ou texto adicional
- Não use markdown (sem ```sql ou ```)
- Gere apenas queries SELECT (nunca INSERT, UPDATE, DELETE ou DROP)
- Use sintaxe válida para PostgreSQL
"""

USER_PROMPT_TEMPLATE = "Pergunta: {pergunta}"

def gerar_sql(pergunta: str) -> str:
    client = Anthropic()
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(pergunta=pergunta)}
        ]
    )
    
    sql = message.content[0].text
    
    return sql.strip()


from sqlalchemy import text
from sqlalchemy.orm import Session

def executar_query(sql: str, db: Session) -> list[dict]:
    
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("A query SQL deve começar com SELECT.")
    
    result = db.execute(text(sql))
    
    columns = result.keys()
    rows = result.fetchall()
    
    results = [dict(zip(columns, row)) for row in rows]
    
    return results