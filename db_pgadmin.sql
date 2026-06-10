CREATE TABLE IF NOT EXISTS usuarios (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100)        NOT NULL,
    email       VARCHAR(150)        UNIQUE NOT NULL,
    senha_hash  VARCHAR(255)        NOT NULL,
    peso_kg     NUMERIC(5, 2),                     
    idade       INTEGER,
    meta_ml     INTEGER DEFAULT 2000,          
    criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CORRIGIDO: Adicionado os textos explicativos dos comentários
COMMENT ON TABLE  usuarios           IS 'Armazena as credenciais e dados antropométricos dos usuários logados';
COMMENT ON COLUMN usuarios.meta_ml   IS 'Meta diária padrão calculada ou definida manualmente pelo usuário';
COMMENT ON COLUMN usuarios.peso_kg   IS 'Peso corporal do usuário em kg utilizado para sugestão de metas';


CREATE TABLE IF NOT EXISTS registros_consumo (
    id           SERIAL PRIMARY KEY,
    usuario_id   INTEGER             NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    quantidade_ml INTEGER            NOT NULL CHECK (quantidade_ml > 0),
    registrado_em TIMESTAMP          DEFAULT CURRENT_TIMESTAMP,
    observacao   TEXT                       -- CORRIGIDO: Removida a vírgula sobressalente daqui
);

COMMENT ON TABLE registros_consumo IS 'Cada linha representa uma ingestão de água registrada pelo usuário';


CREATE TABLE IF NOT EXISTS metas_diarias (
    id            SERIAL PRIMARY KEY,
    usuario_id    INTEGER  NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    data          DATE     NOT NULL DEFAULT CURRENT_DATE,
    meta_ml       INTEGER  NOT NULL,
    consumido_ml  INTEGER  NOT NULL DEFAULT 0,
    atingida      BOOLEAN  GENERATED ALWAYS AS (consumido_ml >= meta_ml) STORED,
    UNIQUE (usuario_id, data)
);

COMMENT ON TABLE metas_diarias IS 'Resumo diário do consumo vs meta por usuário';


-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_registros_usuario_id ON registros_consumo (usuario_id);
CREATE INDEX IF NOT EXISTS idx_registros_data       ON registros_consumo (registrado_em);
CREATE INDEX IF NOT EXISTS idx_metas_usuario_data   ON metas_diarias (usuario_id, data);


-- View de Consumo Diário
CREATE OR REPLACE VIEW vw_consumo_hoje AS
SELECT
    u.id          AS usuario_id,
    u.nome,
    u.meta_ml,
    COALESCE(SUM(r.quantidade_ml), 0)  AS consumido_hoje_ml,
    GREATEST(u.meta_ml - COALESCE(SUM(r.quantidade_ml), 0), 0) AS faltam_ml, -- Evita números negativos se passar da meta
    ROUND(
        (COALESCE(SUM(r.quantidade_ml), 0)::NUMERIC / u.meta_ml) * 100, 1
    )                                  AS percentual
FROM usuarios u
LEFT JOIN registros_consumo r
    ON r.usuario_id = u.id
    AND r.registrado_em::DATE = CURRENT_DATE
GROUP BY u.id, u.nome, u.meta_ml;

COMMENT ON VIEW vw_consumo_hoje IS 'Progresso de hidratação de cada usuário no dia atual';


-- Função/Stored Procedure para Registro de Consumo Automático com Upsert
CREATE OR REPLACE FUNCTION fn_registrar_consumo(
    p_usuario_id  INTEGER,
    p_quantidade  INTEGER,
    p_observacao  TEXT DEFAULT NULL
)
RETURNS TABLE (
    registro_id   INTEGER,
    total_hoje_ml INTEGER,
    meta_ml       INTEGER,
    atingida      BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_registro_id   INTEGER;
    v_meta          INTEGER;
    v_total         INTEGER;
BEGIN
    -- Busca meta do usuário
    SELECT u.meta_ml INTO v_meta FROM usuarios u WHERE u.id = p_usuario_id;

    -- Insere o registro de consumo
    INSERT INTO registros_consumo (usuario_id, quantidade_ml, observacao)
    VALUES (p_usuario_id, p_quantidade, p_observacao)
    RETURNING id INTO v_registro_id;

    -- Calcula total do dia
    SELECT COALESCE(SUM(quantidade_ml), 0) INTO v_total
    FROM registros_consumo
    WHERE usuario_id = p_usuario_id
      AND registrado_em::DATE = CURRENT_DATE;

    -- Upsert na tabela de metas diárias
    INSERT INTO metas_diarias (usuario_id, data, meta_ml, consumido_ml)
    VALUES (p_usuario_id, CURRENT_DATE, v_meta, v_total)
    ON CONFLICT (usuario_id, data)
    DO UPDATE SET consumido_ml = EXCLUDED.consumido_ml;

    RETURN QUERY
    SELECT
        v_registro_id,
        v_total,
        v_meta,
        (v_total >= v_meta);
END;
$$;


-- Inserção de Dados para Teste (Carga Inicial)
INSERT INTO usuarios (nome, email, senha_hash, peso_kg, idade, meta_ml)
VALUES
    ('Socrates Trevisan', 'socrates@email.com', '$2b$10$HASH_EXEMPLO_1', 75.0, 22, 2625),
    ('Maria Silva',      'maria@email.com',    '$2b$10$HASH_EXEMPLO_2', 60.0, 25, 2100),
    ('João Santos',       'joao@email.com',     '$2b$10$HASH_EXEMPLO_3', 80.0, 30, 2800)
ON CONFLICT (email) DO NOTHING;

INSERT INTO registros_consumo (usuario_id, quantidade_ml, observacao)
VALUES
    (1, 300, 'Ao acordar'),
    (1, 500, 'Após treino'),
    (1, 250, 'Com o almoço'),
    (2, 200, 'Manhã'),
    (2, 400, 'À tarde')
ON CONFLICT DO NOTHING;


-- Bloco de testes para rodar no pgAdmin e validar os resultados:
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

SELECT * FROM vw_consumo_hoje;

SELECT * FROM fn_registrar_consumo(1, 300, 'Teste via pgAdmin');

SELECT * FROM vw_consumo_hoje;