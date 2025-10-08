from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import sqlite3
import os

DB_PATH = os.getenv("EMP_DB", "empleos.db")

app = FastAPI(
    title="API Empleos",
    version="1.1.0"
)

class Modalidad(str, Enum):
    remoto = "Remoto"
    hibrido = "Híbrido"
    presencial = "Presencial"

class TipoContrato(str, Enum):
    tc = "Tiempo Completo"
    mt = "Medio Tiempo"
    fl = "Freelance"
    pr = "Prácticas"

class JobIn(BaseModel):
    titulo: str = Field(..., min_length=3)
    empresa: str = Field(..., min_length=2)
    ubicacion: str = Field(..., min_length=2)
    modalidad: Modalidad
    tipo: TipoContrato
    salario_min: float = Field(..., ge=0)
    salario_max: float = Field(..., ge=0)
    descripcion: str = Field(..., min_length=10)
    publicada_en: datetime

    def model_post_init(self, _):
        if self.salario_min > self.salario_max:
            raise ValueError("salario_min no puede ser mayor que salario_max")

class JobOut(JobIn):
    id: int

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS empleos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            empresa TEXT NOT NULL,
            ubicacion TEXT NOT NULL,
            modalidad TEXT NOT NULL,
            tipo TEXT NOT NULL,
            salario_min REAL NOT NULL,
            salario_max REAL NOT NULL,
            descripcion TEXT NOT NULL,
            publicada_en TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

ensure_db()

def row_to_job(row: sqlite3.Row) -> JobOut:
    return JobOut(
        id=row["id"],
        titulo=row["titulo"],
        empresa=row["empresa"],
        ubicacion=row["ubicacion"],
        modalidad=row["modalidad"],
        tipo=row["tipo"],
        salario_min=row["salario_min"],
        salario_max=row["salario_max"],
        descripcion=row["descripcion"],
        publicada_en=datetime.fromisoformat(row["publicada_en"]),
    )

@app.get("/")
def root():
    return {"message": "API Empleos OK", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/jobs", response_model=List[JobOut])
def listar_jobs(
    q: Optional[str] = Query(None),
    modalidad: Optional[Modalidad] = None,
    tipo: Optional[TipoContrato] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    base_sql = """
        SELECT id, titulo, empresa, ubicacion, modalidad, tipo,
               salario_min, salario_max, descripcion, publicada_en
        FROM empleos
    """
    where = []
    params: List[object] = []

    if q:
        where.append("(titulo LIKE ? OR empresa LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like])

    if modalidad:
        where.append("modalidad = ?")
        params.append(modalidad.value)

    if tipo:
        where.append("tipo = ?")
        params.append(tipo.value)

    if where:
        base_sql += " WHERE " + " AND ".join(where)

    base_sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([page_size, (page - 1) * page_size])

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(base_sql, params)
    rows = cur.fetchall()
    conn.close()

    return [row_to_job(r) for r in rows]

@app.get("/jobs/{job_id}", response_model=JobOut)
def obtener_job(job_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, titulo, empresa, ubicacion, modalidad, tipo,
               salario_min, salario_max, descripcion, publicada_en
        FROM empleos WHERE id = ?
        """,
        (job_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Empleo no encontrado")
    return row_to_job(row)

@app.post("/jobs", response_model=JobOut, status_code=201)
def crear_job(data: JobIn):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO empleos
        (titulo, empresa, ubicacion, modalidad, tipo, salario_min, salario_max, descripcion, publicada_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.titulo,
            data.empresa,
            data.ubicacion,
            data.modalidad.value,
            data.tipo.value,
            float(data.salario_min),
            float(data.salario_max),
            data.descripcion,
            data.publicada_en.isoformat(),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.execute(
        """
        SELECT id, titulo, empresa, ubicacion, modalidad, tipo,
               salario_min, salario_max, descripcion, publicada_en
        FROM empleos WHERE id = ?
        """,
        (new_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row_to_job(row)

@app.put("/jobs/{job_id}", response_model=JobOut)
def actualizar_job(job_id: int, data: JobIn):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM empleos WHERE id = ?", (job_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Empleo no encontrado")

    cur.execute(
        """
        UPDATE empleos
        SET titulo = ?, empresa = ?, ubicacion = ?, modalidad = ?, tipo = ?,
            salario_min = ?, salario_max = ?, descripcion = ?, publicada_en = ?
        WHERE id = ?
        """,
        (
            data.titulo,
            data.empresa,
            data.ubicacion,
            data.modalidad.value,
            data.tipo.value,
            float(data.salario_min),
            float(data.salario_max),
            data.descripcion,
            data.publicada_en.isoformat(),
            job_id,
        ),
    )
    conn.commit()
    cur.execute(
        """
        SELECT id, titulo, empresa, ubicacion, modalidad, tipo,
               salario_min, salario_max, descripcion, publicada_en
        FROM empleos WHERE id = ?
        """,
        (job_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row_to_job(row)

@app.delete("/jobs/{job_id}", status_code=204)
def eliminar_job(job_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM empleos WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
