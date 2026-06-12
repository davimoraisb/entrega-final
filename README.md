# Controle de Hidratação

Sistema desenvolvido em Python com Flask e PostgreSQL para monitoramento da ingestão diária de água. A aplicação permite cadastrar usuários, registrar consumos, acompanhar metas diárias e consultar o histórico de hidratação.

## Objetivo

Este projeto foi desenvolvido como trabalho final da disciplina, aplicando conceitos de:

- Desenvolvimento colaborativo com Git e GitHub;
- Pull Requests e Code Review;
- Banco de dados relacional;
- Testes automatizados;
- Integração Contínua com GitHub Actions;
- Persistência de dados em banco PostgreSQL;
- Boas práticas de desenvolvimento de software.

---

## Tecnologias Utilizadas

### Backend

- Python 3.11+
- Flask 3.0.3
- Bcrypt

### Banco de Dados

- PostgreSQL
- PL/pgSQL

### Testes

- Pytest

### DevOps

- GitHub
- GitHub Actions

### Bibliotecas

- psycopg2-binary
- python-dotenv
- gunicorn

---

## Requisitos

### Versão recomendada do Python

O projeto foi desenvolvido e testado utilizando Python 3.12.

Versões recomendadas:

- Python 3.11
- Python 3.12

Versões mais recentes, como Python 3.14, podem apresentar incompatibilidades com algumas dependências, especialmente com `psycopg2-binary`.

---

## Estrutura do Projeto

```text
entrega-final
│
├── app.py
├── db.py
├── db_pgadmin.sql
├── test.py
├── requirements.txt
├── README.md
└── .github
    └── workflows
        └── ci.yml
```

---

## Funcionalidades

### Usuários

- Cadastro de usuários;
- Login com senha criptografada utilizando Bcrypt;
- Definição automática da meta diária de hidratação;
- Atualização da meta personalizada.

### Consumo de Água

- Registro das ingestões realizadas ao longo do dia;
- Observações opcionais para cada consumo;
- Cálculo automático do total consumido.

### Acompanhamento Diário

- Quantidade total consumida;
- Percentual da meta atingido;
- Quantidade restante para alcançar a meta.

### Histórico

- Consulta dos últimos dias;
- Registro das metas atingidas;
- Histórico consolidado de consumo.

---

## Modelagem do Banco de Dados

### Tabelas

#### usuarios

Armazena os dados e credenciais dos usuários.

#### registros_consumo

Armazena cada registro individual de ingestão de água.

#### metas_diarias

Armazena o resumo diário do consumo e das metas dos usuários.

---

### View

#### vw_consumo_hoje

Responsável por consolidar o consumo diário dos usuários, retornando:

- Meta diária;
- Quantidade consumida;
- Quantidade restante;
- Percentual atingido.

---

### Stored Procedure

#### fn_registrar_consumo()

Responsável por:

1. Registrar uma nova ingestão de água;
2. Calcular o total consumido no dia;
3. Atualizar automaticamente a tabela de metas diárias;
4. Informar se a meta diária foi atingida.

---

## Instalação

### Clonar o repositório

```bash
git clone https://github.com/davimoraisb/entrega-final.git
```

### Entrar na pasta do projeto

```bash
cd entrega-final
```

### Criar um ambiente virtual

Windows:

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Atualizar o pip

```bash
python -m pip install --upgrade pip
```

### Instalar as dependências

```bash
pip install -r requirements.txt
```

---

## Configuração do Banco de Dados

Configure as variáveis de ambiente:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hidratacao_db
DB_USER=postgres
DB_PASSWORD=postgres
```

Execute o script SQL:

```bash
psql -U postgres -d hidratacao_db -f db_pgadmin.sql
```

---

## Executando a Aplicação

```bash
python app.py
```

A aplicação estará disponível em:

```text
http://localhost:5000
```

---

## Endpoints

### Cadastro de Usuário

```http
POST /usuarios
```

Body:

```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "123456",
  "peso_kg": 75,
  "idade": 25
}
```

---

### Login

```http
POST /login
```

Body:

```json
{
  "email": "joao@email.com",
  "senha": "123456"
}
```

---

### Registrar Consumo

```http
POST /consumo
```

Body:

```json
{
  "usuario_id": 1,
  "quantidade_ml": 500,
  "observacao": "Após o treino"
}
```

---

### Consultar Consumos do Dia

```http
GET /consumo/{usuario_id}/hoje
```

---

### Consultar Progresso Diário

```http
GET /consumo/{usuario_id}/progresso
```

---

### Consultar Histórico

```http
GET /consumo/{usuario_id}/historico
```

---

### Atualizar Meta

```http
PUT /usuarios/{usuario_id}/meta
```

Body:

```json
{
  "meta_ml": 3000
}
```

---

### Verificar Saúde da Aplicação

```http
GET /health
```

---

## Testes

Para executar os testes automatizados:

```bash
pytest test.py -v
```

Os testes verificam:

- Conexão com o banco de dados;
- Cadastro de usuários;
- Busca por e-mail;
- Registro de consumo;
- Progresso diário;
- Atualização de metas;
- Histórico de consumo.

---

## Integração Contínua

O projeto utiliza GitHub Actions para:

- Instalação automática das dependências;
- Inicialização de um banco PostgreSQL temporário;
- Criação das tabelas do sistema;
- Execução dos testes automatizados;
- Validação dos Pull Requests antes do merge.

---

## Equipe de Desenvolvimento

| Nome | GitHub |
|--------|--------|
| Arthur Galvão |  |
| Arthur Machado | https://github.com/amachado2006 |
| Artur Nemer | https://github.com/ArturCosta-coder |
| Davi Morais | https://github.com/davimoraisb |
| Socrates  |  |

## Desenvolvimento Colaborativo

O projeto foi desenvolvido utilizando:

- Branches;
- Pull Requests;
- Code Review;
- GitHub Actions;
- Controle de versão com Git.

---

## Estrutura da API

| Método | Endpoint | Descrição |
|----------|----------|----------|
| POST | `/usuarios` | Cadastro de usuários |
| POST | `/login` | Autenticação |
| POST | `/consumo` | Registro de consumo |
| GET | `/consumo/<usuario_id>/hoje` | Consumos do dia |
| GET | `/consumo/<usuario_id>/progresso` | Progresso diário |
| GET | `/consumo/<usuario_id>/historico` | Histórico do usuário |
| PUT | `/usuarios/<usuario_id>/meta` | Atualização da meta |
| GET | `/health` | Verificação da aplicação |

---

## Repositório

https://github.com/davimoraisb/entrega-final

---

## Licença

Projeto desenvolvido para fins acadêmicos.