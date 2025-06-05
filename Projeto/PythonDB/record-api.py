from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel, ConfigDict
from typing import List
import logging
from contextlib import asynccontextmanager

#--------------------------------------------------------

# tem que alterar as infos aqui pra rodar em outra máquina

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from urllib.parse import quote_plus
password = "123456"
DATABASE_URL = f"postgresql+psycopg2://postgres:{quote_plus(password)}@localhost:5432/postgres"

# tem que alterar as infos aqui----------^^^^^^^^^^^---------pra rodar em outra máquina

#--------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message = Column(String(500), nullable=False)
    user_id_send = Column(Integer, nullable=False)
    user_id_receive = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())

class MessageCreate(BaseModel):
    message: str
    user_id_send: int
    user_id_receive: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Olá, como vai você?",
                "user_id_send": 1,
                "user_id_receive": 2
            }
        }
    )

class MessageResponse(BaseModel):
    message_id: int
    message: str
    user_id_send: int
    user_id_receive: int
    timestamp: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise
    yield
    

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    try:
        db_message = Message(
            message=message.message,
            user_id_send=message.user_id_send,
            user_id_receive=message.user_id_receive
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        logger.info(f"Mensagem criada com ID: {db_message.message_id}")
        
        return {
            "message_id": db_message.message_id,
            "message": db_message.message,
            "user_id_send": db_message.user_id_send,
            "user_id_receive": db_message.user_id_receive,
            "timestamp": db_message.timestamp.isoformat()
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar mensagem: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a mensagem"
        )

@app.get("/messages/{user_id_send}/{user_id_receive}", response_model=List[MessageResponse])
def read_messages(user_id_send: int, user_id_receive: int, db: Session = Depends(get_db)):
    try:
        messages = db.query(Message).filter(
            ((Message.user_id_send == user_id_send) & (Message.user_id_receive == user_id_receive)) |
            ((Message.user_id_send == user_id_receive) & (Message.user_id_receive == user_id_send))
        ).order_by(Message.timestamp).all()
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma mensagem encontrada"
            )
        return [
            MessageResponse.model_validate({
                **m.__dict__,
                "timestamp": m.timestamp.isoformat()
            })
            for m in messages
        ]
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a requisição"
        )

@app.get("/")
def health_check():
    return {"status": "OK", "message": "API de Mensagens está funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("record-api:app", host="127.0.0.1", port=8000, reload=True)
