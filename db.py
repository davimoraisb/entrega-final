# db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Pega a URL do banco da nuvem ou monta uma local
# Exemplo de DATABASE_URL: "postgresql://usuario:senha@host:port/database"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/controle_hidratacao")

def get_conexao():
    """Retorna uma conexão ativa com o PostgreSQL usando RealDictCursor"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def testar_conexao():
    """Verifica se a aplicação consegue se conectar ao PostgreSQL (Resolve o AttributeError)"""
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        print(" [BD] Conexão com o PostgreSQL estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ [BD] Erro ao conectar ao banco de dados: {e}")
        return False

def criar_usuario(nome, email, senha_hash, peso_kg=None, idade=None):
    """Insere um novo usuário e calcula a meta sugerida se não fornecida"""
    # Meta sugerida: 35ml por kg. Se não tiver peso, adota 2000ml padrão
    meta_sugerida = int(peso_kg * 35) if peso_kg else 2000
    
    conn = get_conexao()
    cursor = conn.cursor()
    query = """
        INSERT INTO usuarios (nome, email, senha_hash, peso_kg, idade, meta_ml)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, nome, email, peso_kg, idade, meta_ml, criado_em;
    """
    cursor.execute(query, (nome, email, senha_hash, peso_kg, idade, meta_sugerida))
    usuario = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return usuario

def buscar_usuario_por_email(email):
    """Busca um usuário por e-mail para o fluxo de Login"""
    conn = get_conexao()
    cursor = conn.cursor()
    query = "SELECT id, nome, email, senha_hash, peso_kg, idade, meta_ml FROM usuarios WHERE email = %s;"
    cursor.execute(query, (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario

def registrar_consumo(usuario_id, quantidade_ml, observacao=None):
    """Chama a Stored Procedure 'fn_registrar_consumo' criada no PostgreSQL"""
    conn = get_conexao()
    cursor = conn.cursor()
    
    # Executa a função que criamos no banco de dados
    query = "SELECT * FROM fn_registrar_consumo(%s, %s, %s);"
    cursor.execute(query, (usuario_id, quantidade_ml, observacao))
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
    """Lista todos os registros individuais de consumo de água feitos hoje pelo usuário"""
    conn = get_conexao()
    cursor = conn.cursor()
    query = """
        SELECT id, quantidade_ml, registrado_em, observacao 
        FROM registros_consumo 
        WHERE usuario_id = %s AND registrado_em::DATE = CURRENT_DATE
        ORDER BY registrado_em DESC;
    """
    cursor.execute(query, (usuario_id,))
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return registros

def get_progresso_usuario(usuario_id):
    """Consulta a View 'vw_consumo_hoje' para trazer o painel do dia atual"""
    conn = get_conexao()
    cursor = conn.cursor()
    query = "SELECT * FROM vw_consumo_hoje WHERE usuario_id = %s;"
    cursor.execute(query, (usuario_id,))
    progresso = cursor.fetchone()
    cursor.close()
    conn.close()
    return progresso

def get_historico(usuario_id, dias=7):
    """Busca o consolidado histórico de consumo vs metas dos últimos X dias"""
    conn = get_conexao()
    cursor = conn.cursor()
    query = """
        SELECT data, meta_ml, consumido_ml, atingida 
        FROM metas_diarias 
        WHERE usuario_id = %s AND data >= CURRENT_DATE - %s
        ORDER BY data DESC;
    """
    cursor.execute(query, (usuario_id, dias))
    historico_dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return historico_dados

def atualizar_meta(usuario_id, nova_meta):
    """Atualiza a meta cadastral do usuário no perfil"""
    conn = get_conexao()
    cursor = conn.cursor()
    query = "UPDATE usuarios SET meta_ml = %s WHERE id = %s RETURNING id, nome, meta_ml;"
    cursor.execute(query, (nova_meta, usuario_id))
    resultado = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return resultado