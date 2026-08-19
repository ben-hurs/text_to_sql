from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas import PerguntaRequest, RespostaQuery
from src.nl_sql_engine import gerar_sql, executar_query

router = APIRouter()

@router.post("/ask-natural-language", response_model=RespostaQuery)
def ask_natural_language(request: PerguntaRequest, db: Session = Depends(get_db)):
    sql_gerado = gerar_sql(request.pergunta)
    
    try:
        resultados = executar_query(sql_gerado, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    resposta = RespostaQuery(
        pergunta=request.pergunta,
        sql_gerado=sql_gerado,
        resultados=resultados,
        total_registros=len(resultados)
    )
    return resposta