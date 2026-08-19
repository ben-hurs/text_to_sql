from pydantic import BaseModel
from typing import Dict, List, Any

class PerguntaRequest(BaseModel):
    pergunta: str
    

class RespostaQuery(BaseModel):
    pergunta: str
    sql_gerado: str
    resultados: List[Dict[str, Any]] 
    total_registros: int