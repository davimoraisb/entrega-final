import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hidratacao_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def get_conexao():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def testar_conexao():
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False


def criar_usuario(nome, email, senha_hash, peso_kg=None, idade=None):
    meta_sugerida = int(peso_kg * 35) if peso_kg else 2000

    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, senha_hash, peso_kg, idade, meta_ml)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, nome, email, peso_kg, idade, meta_ml, criado_em;
        """,
        (nome, email, senha_hash, peso_kg, idade, meta_sugerida)
    )

    usuario = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return usuario


def buscar_usuario_por_email(email):
    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, nome, email, senha_hash, peso_kg, idade, meta_ml
        FROM usuarios
        WHERE email = %s;
        """,
        (email,)
    )

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    return usuario


def registrar_consumo(usuario_id, quantidade_ml, observacao=None):
    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM fn_registrar_consumo(%s, %s, %s);
        """,
        (usuario_id, quantidade_ml, observacao)
    )

    resultado = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "registro_id": resultado["registro_id"],
        "total_hoje_ml": resultado["total_hoje_ml"],
        "meta_ml": resultado["meta_ml"],
        "atingida": resultado["atingida"]
    }


def get_consumo_hoje(usuario_id):
    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, quantidade_ml, registrado_em, observacao
        FROM registros_consumo
        WHERE usuario_id = %s
        AND registrado_em::DATE = CURRENT_DATE
        ORDER BY registrado_em DESC;
        """,
        (usuario_id,)
    )

    registros = cursor.fetchall()

    cursor.close()
    conn.close()

    return registros


def get_progresso_usuario(usuario_id):
    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM vw_consumo_hoje
        WHERE usuario_id = %s;
        """,
        (usuario_id,)
    )

    progresso = cursor.fetchone()

    cursor.close()
    conn.close()

    return progresso


def get_historico(usuario_id, dias=7):
    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT data, meta_ml, consumido_ml, atingida
        FROM metas_diarias
        WHERE usuario_id = %s
        AND data >= CURRENT_DATE - %s
        ORDER BY data DESC;
        """,
        (usuario_id, dias)
    )

    historico = cursor.fetchall()

    cursor.close()
    conn.close()

    return historico


def atualizar_meta(usuario_id, nova_meta):
    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE usuarios
        SET meta_ml = %s
        WHERE id = %s
        RETURNING id, nome, meta_ml;
        """,
        (nova_meta, usuario_id)
    )

    resultado = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return resultado