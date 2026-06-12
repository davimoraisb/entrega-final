import os
import time
import pytest

os.environ.setdefault("DB_NAME", "hidratacao_db")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "postgres")

import db

EMAIL_TESTE = f"teste_{int(time.time())}@email.com"



@pytest.fixture(scope="module")
def usuario_criado():
    """Cria um usuário de teste e retorna seus dados."""
    usuario = db.criar_usuario(
        nome="Usuário Teste",
        email=EMAIL_TESTE,
        senha_hash="$2b$10$hash_falso_para_teste",
        peso_kg=70.0,
        idade=25,
    )
    assert usuario["id"] is not None
    return usuario


def test_conexao_banco():
    """O banco deve estar acessível."""
    assert db.testar_conexao() is True


def test_criar_usuario(usuario_criado):
    """Deve criar um usuário e calcular a meta corretamente (70kg × 35 = 2450ml)."""
    assert usuario_criado["nome"] == "Usuário Teste"
    assert usuario_criado["email"] == EMAIL_TESTE
    assert usuario_criado["meta_ml"] == 2450


def test_buscar_usuario_por_email(usuario_criado):
    """Deve encontrar o usuário pelo e-mail."""
    usuario = db.buscar_usuario_por_email(EMAIL_TESTE)
    assert usuario is not None
    assert usuario["id"] == usuario_criado["id"]


def test_buscar_usuario_inexistente():
    """Deve retornar None para e-mail não cadastrado."""
    resultado = db.buscar_usuario_por_email("naoexiste@email.com")
    assert resultado is None


def test_registrar_consumo(usuario_criado):
    """Deve registrar consumo e retornar o progresso do dia."""
    resultado = db.registrar_consumo(
        usuario_id=usuario_criado["id"],
        quantidade_ml=500,
        observacao="Teste pytest"
    )
    assert resultado["registro_id"] is not None
    assert resultado["total_hoje_ml"] >= 500
    assert resultado["meta_ml"] == 2450
    assert isinstance(resultado["atingida"], bool)


def test_consumo_hoje_nao_vazio(usuario_criado):
    """Deve retornar pelo menos um registro de hoje."""
    registros = db.get_consumo_hoje(usuario_criado["id"])
    assert isinstance(registros, list)
    assert len(registros) >= 1
    assert registros[0]["quantidade_ml"] > 0


def test_progresso_usuario(usuario_criado):
    """Deve retornar o progresso com todos os campos esperados."""
    progresso = db.get_progresso_usuario(usuario_criado["id"])
    assert progresso is not None
    assert "consumido_hoje_ml" in progresso
    assert "meta_ml" in progresso
    assert "percentual" in progresso
    assert progresso["consumido_hoje_ml"] >= 500


def test_atualizar_meta(usuario_criado):
    """Deve atualizar a meta diária do usuário."""
    resultado = db.atualizar_meta(usuario_criado["id"], 3000)
    assert resultado is not None
    assert resultado["meta_ml"] == 3000


def test_historico(usuario_criado):
    """Deve retornar o histórico (pode ser vazio se for o primeiro dia)."""
    historico = db.get_historico(usuario_criado["id"], dias=7)
    assert isinstance(historico, list)