# app/data_apis/otimizacoes.py
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

def bulk_upsert(session: Session, model, records):
    """
    Realiza inserção ou atualização em lote de forma eficiente
    """
    if not records:
        return
    
    stmt = insert(model).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=['data'],  # Coluna de identificação única
        set_={
            'valor': stmt.excluded.valor,
            # Outros campos para atualizar
        }
    )
    session.execute(stmt)
    session.commit()