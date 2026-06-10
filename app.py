from flask import Flask, request, jsonify
import bcrypt
import db

app = Flask(__name__)



@app.route("/usuarios", methods=["POST"])
def cadastrar_usuario():
    """
    POST /usuarios
    Body JSON: { "nome", "email", "senha", "peso_kg", "idade" }
    """
    dados = request.get_json()

    campos_obrigatorios = ["nome", "email", "senha"]
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            return jsonify({"erro": f"Campo '{campo}' é obrigatório"}), 400

    # Gera o hash da senha com bcrypt
    senha_hash = bcrypt.hashpw(
        dados["senha"].encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    try:
        usuario = db.criar_usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha_hash=senha_hash,
            peso_kg=dados.get("peso_kg"),
            idade=dados.get("idade"),
        )
        return jsonify(usuario), 201
    except Exception as e:
        if "unique" in str(e).lower():
            return jsonify({"erro": "E-mail já cadastrado"}), 409
        return jsonify({"erro": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    """
    POST /login
    Body JSON: { "email", "senha" }
    """
    dados = request.get_json()
    usuario = db.buscar_usuario_por_email(dados.get("email", ""))

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    senha_correta = bcrypt.checkpw(
        dados["senha"].encode("utf-8"),
        usuario["senha_hash"].encode("utf-8")
    )
    if not senha_correta:
        return jsonify({"erro": "Senha incorreta"}), 401

    # Retorna sem expor o hash da senha
    usuario.pop("senha_hash", None)
    return jsonify({"mensagem": "Login realizado com sucesso", "usuario": usuario}), 200



@app.route("/consumo", methods=["POST"])
def registrar_consumo():
    """
    POST /consumo
    Body JSON: { "usuario_id", "quantidade_ml", "observacao" (opcional) }
    Retorna: progresso atual do dia
    """
    dados = request.get_json()

    if not dados.get("usuario_id") or not dados.get("quantidade_ml"):
        return jsonify({"erro": "usuario_id e quantidade_ml são obrigatórios"}), 400

    try:
        resultado = db.registrar_consumo(
            usuario_id=dados["usuario_id"],
            quantidade_ml=dados["quantidade_ml"],
            observacao=dados.get("observacao"),
        )
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/consumo/<int:usuario_id>/hoje", methods=["GET"])
def consumo_hoje(usuario_id):
    """GET /consumo/<usuario_id>/hoje — lista os registros de hoje"""
    registros = db.get_consumo_hoje(usuario_id)
    return jsonify(registros), 200


@app.route("/consumo/<int:usuario_id>/progresso", methods=["GET"])
def progresso(usuario_id):
    """GET /consumo/<usuario_id>/progresso — progresso atual do dia"""
    dados = db.get_progresso_usuario(usuario_id)
    if not dados:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify(dados), 200


@app.route("/consumo/<int:usuario_id>/historico", methods=["GET"])
def historico(usuario_id):
    """GET /consumo/<usuario_id>/historico?dias=7 — histórico dos últimos dias"""
    dias = int(request.args.get("dias", 7))
    dados = db.get_historico(usuario_id, dias)
    return jsonify(dados), 200



@app.route("/usuarios/<int:usuario_id>/meta", methods=["PUT"])
def atualizar_meta(usuario_id):
    """
    PUT /usuarios/<usuario_id>/meta
    Body JSON: { "meta_ml": 2500 }
    """
    dados = request.get_json()
    nova_meta = dados.get("meta_ml")

    if not nova_meta or nova_meta <= 0:
        return jsonify({"erro": "meta_ml deve ser um número positivo"}), 400

    resultado = db.atualizar_meta(usuario_id, nova_meta)
    if not resultado:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    return jsonify(resultado), 200



@app.route("/health", methods=["GET"])
def health():
    ok = db.testar_conexao()
    status = "ok" if ok else "erro"
    code = 200 if ok else 503
    return jsonify({"status": status, "banco": "PostgreSQL"}), code



if __name__ == "__main__":
    db.testar_conexao()
    app.run(debug=True, port=5000)