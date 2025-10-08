from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import sqlite3

app = FastAPI(title="API Empleos", version="1.0.0")

DB_PATH = "empleos.db"


# -------- Modelos --------
class Job(BaseModel):
    titulo: str = Field(..., min_length=3)
    empresa: str = Field(..., min_length=2)
    ubicacion: str = Field(..., min_length=2)
    modalidad: str = Field(..., pattern="^(Remoto|Híbrido|Presencial)$")
    tipo: str = Field(..., pattern="^(Tiempo Completo|Medio Tiempo|Freelance|Prácticas)$")
    salario_min: float = Field(..., ge=0)
    salario_max: float = Field(..., ge=0)
    descripcion: str = Field(..., min_length=10)
    publicada_en: datetime


# -------- Funciones auxiliares --------
def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS empleos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            empresa TEXT,
            ubicacion TEXT,
            modalidad TEXT,
            tipo TEXT,
            salario_min REAL,
            salario_max REAL,
            descripcion TEXT,
            publicada_en TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


def row_to_dict(row):
    return {
        "id": row[0],
        "titulo": row[1],
        "empresa": row[2],
        "ubicacion": row[3],
        "modalidad": row[4],
        "tipo": row[5],
        "salario_min": row[6],
        "salario_max": row[7],
        "descripcion": row[8],
        "publicada_en": row[9]
    }


# -------- Endpoints --------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/jobs")
def listar_jobs(q: Optional[str] = Query(None, description="Filtra por título o empresa")):
    conn = get_conn()
    cur = conn.cursor()
    if q:
        like = f"%{q}%"
        cur.execute("SELECT * FROM empleos WHERE titulo LIKE ? OR empresa LIKE ?", (like, like))
    else:
        cur.execute("SELECT * FROM empleos")
    rows = cur.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@app.get("/jobs/{job_id}")
def obtener_job(job_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM empleos WHERE id=?", (job_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Empleo no encontrado")
    return row_to_dict(row)


@app.post("/jobs", status_code=201)
def crear_job(job: Job):
    if job.salario_min > job.salario_max:
        raise HTTPException(status_code=400, detail="El salario mínimo no puede ser mayor que el máximo")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO empleos (titulo, empresa, ubicacion, modalidad, tipo, salario_min, salario_max, descripcion, publicada_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (job.titulo, job.empresa, job.ubicacion, job.modalidad, job.tipo,
          job.salario_min, job.salario_max, job.descripcion, job.publicada_en.isoformat()))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, **job.dict()}


@app.put("/jobs/{job_id}")
def actualizar_job(job_id: int, job: Job):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM empleos WHERE id=?", (job_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Empleo no encontrado")
    cur.execute("""
        UPDATE empleos SET titulo=?, empresa=?, ubicacion=?, modalidad=?, tipo=?,
        salario_min=?, salario_max=?, descripcion=?, publicada_en=?
        WHERE id=?
    """, (job.titulo, job.empresa, job.ubicacion, job.modalidad, job.tipo,
          job.salario_min, job.salario_max, job.descripcion, job.publicada_en.isoformat(), job_id))
    conn.commit()
    conn.close()
    return {"mensaje": "Empleo actualizado correctamente"}


@app.delete("/jobs/{job_id}", status_code=204)
def eliminar_job(job_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM empleos WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Empleo eliminado"}