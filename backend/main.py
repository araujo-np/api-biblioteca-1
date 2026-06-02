from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS (SQLAlchemy)
# ==========================================
# Cria o arquivo do banco de dados chamado 'banco.db' na mesma pasta
DATABASE_URL = "sqlite:///./banco.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo do Banco de Dados (Como a tabela será criada no SQLite)
class LivroDB(Base): 
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    url_imagem = Column(String, nullable=False) # Link da imagem salvo no banco
    disponivel = Column(Boolean, default=True)

# Cria a tabela no banco de dados se ela não existir
Base.metadata.create_all(bind=engine)

# Função auxiliar para abrir/fechar a conexão com o banco a cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# CONFIGURAÇÃO DO FASTAPI (Schemas e Rotas)
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Esquema do Pydantic (Para validar os dados que entram e saem da API)
class LivroSchema(BaseModel):
    titulo: str
    autor: str
    url_imagem: str
    disponivel: bool = True

    class Config:
        from_attributes = True


# --- ROTAS DA API ---

# 1. Listar todos os livros do banco
@app.get("/livros")
def listar_livros(db: Session = Depends(get_db)):
    livros = db.query(LivroDB).all()
    return livros

# 2. Buscar um livro pelo ID no banco
@app.get("/livros/{id}")
def buscar_livro(id: int, db: Session = Depends(get_db)):
    livro = db.query(LivroDB).filter(LivroDB.id == id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro

# 3. Adicionar um novo livro no banco (com a URL da imagem)
@app.post("/livros", status_code=status.HTTP_201_CREATED)
def adicionar_livro(livro: LivroSchema, db: Session = Depends(get_db)):
    # Criamos a linha do banco usando os dados enviados pelo frontend
    novo_livro = LivroDB(
        titulo=livro.titulo,
        autor=livro.autor,
        url_imagem=livro.url_imagem,
        disponivel=livro.disponivel
    )
    db.add(novo_livro) # Coloca na fila do banco
    db.commit()        # Salva permanentemente no banco
    db.refresh(novo_livro) # Atualiza o objeto com o ID gerado automaticamente
    return {"mensagem": "Livro adicionado com sucesso!", "livro": novo_livro}

# 4. Atualizar um livro no banco
@app.put("/livros/{id}")
def atualizar_livro(id: int, novo_conteudo: LivroSchema, db: Session = Depends(get_db)):
    livro_existente = db.query(LivroDB).filter(LivroDB.id == id).first()
    if not livro_existente:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    # Atualiza campo por campo
    livro_existente.titulo = novo_conteudo.titulo
    livro_existente.autor = novo_conteudo.autor
    livro_existente.url_imagem = novo_conteudo.url_imagem
    livro_existente.disponivel = novo_conteudo.disponivel

    db.commit()
    db.refresh(livro_existente)
    return {"mensagem": "Livro atualizado com sucesso!", "livro": livro_existente}

# 5. Excluir um livro do banco
@app.delete("/livros/{id}")
def excluir_livro(id: int, db: Session = Depends(get_db)):
    livro = db.query(LivroDB).filter(LivroDB.id == id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db.delete(livro)
    db.commit()
    return {"mensagem": "Livro removido com sucesso!"}

#teste