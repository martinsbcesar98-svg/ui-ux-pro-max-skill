import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "barbearia.db")

BARBEIROS = {
    "arthur": {"nome": "Arthur Tungo", "senha": "arthur123"},
    "klein": {"nome": "Klein", "senha": "klein123"},
    "vemba": {"nome": "Vemba", "senha": "vemba123"},
    "bernardo": {"nome": "Bernardo", "senha": "bernardo123"},
    "baldie": {"nome": "Baldie", "senha": "baldie123"},
}

SERVICOS = {
    "corte_pedrinho": {"nome": "Corte Pedrinho (Cabelo, Barba e Limpeza Facial)", "preco": 11000.00},
    "corte_frances_2t": {"nome": "Corte Francês (2 Tempos)", "preco": 6000.00},
    "corte_frances_jr": {"nome": "Corte Francês (Júnior)", "preco": 5000.00},
    "corte_escovinha_adulto": {"nome": "Corte Escovinha (Adulto)", "preco": 5500.00},
    "corte_escovinha_jr": {"nome": "Corte Escovinha (Júnior)", "preco": 5000.00},
    "pintura_curto": {"nome": "Pintura de Cabelo Curto", "preco": 6000.00},
    "pintura_medio": {"nome": "Pintura de Cabelo Médio", "preco": 17000.00},
    "desfriso_curto": {"nome": "Desfriso de Cabelo Curto", "preco": 6000.00},
    "limpeza_facial": {"nome": "Limpeza Facial", "preco": 6750.00},
    "laminagem": {"nome": "Laminagem", "preco": 3000.00},
    "barba_bigode": {"nome": "Barba e Bigode", "preco": 3000.00},
    "barba_depilador": {"nome": "Barba com Depilador", "preco": 7750.00},
    "corte_depilador": {"nome": "Corte de Cabelo c/ Depilador", "preco": 11000.00},
    "desenho": {"nome": "Desenho", "preco": 3000.00},
    "grafite": {"nome": "Grafite", "preco": 5300.00},
}

COMISSAO_PERCENTUAL = 0.20


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS barbeiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            criado_em TEXT DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cortes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barbeiro_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            servico_key TEXT NOT NULL,
            servico_nome TEXT NOT NULL,
            valor REAL NOT NULL,
            observacao TEXT,
            criado_em TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (barbeiro_id) REFERENCES barbeiros(id)
        )
    """)

    for username, dados in BARBEIROS.items():
        senha_hash = hash_senha(dados["senha"])
        cur.execute("""
            INSERT OR IGNORE INTO barbeiros (username, nome, senha_hash)
            VALUES (?, ?, ?)
        """, (username, dados["nome"], senha_hash))

    conn.commit()
    conn.close()


def autenticar(username: str, senha: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM barbeiros WHERE username = ?", (username.lower(),))
    barbeiro = cur.fetchone()
    conn.close()

    if barbeiro and barbeiro["senha_hash"] == hash_senha(senha):
        return dict(barbeiro)
    return None


def registrar_corte(barbeiro_id: int, data: str, servico_key: str, valor: float, observacao: str = ""):
    servico = SERVICOS.get(servico_key)
    if not servico:
        raise ValueError(f"Serviço '{servico_key}' não encontrado.")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO cortes (barbeiro_id, data, servico_key, servico_nome, valor, observacao)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (barbeiro_id, data, servico_key, servico["nome"], valor, observacao))
    conn.commit()
    conn.close()


def obter_cortes(barbeiro_id: int, mes: int = None, ano: int = None):
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM cortes WHERE barbeiro_id = ?"
    params = [barbeiro_id]

    if mes and ano:
        query += " AND strftime('%m', data) = ? AND strftime('%Y', data) = ?"
        params += [f"{mes:02d}", str(ano)]

    query += " ORDER BY data DESC, criado_em DESC"
    cur.execute(query, params)
    cortes = [dict(r) for r in cur.fetchall()]
    conn.close()
    return cortes


def calcular_resumo_mensal(barbeiro_id: int, mes: int, ano: int) -> dict:
    cortes = obter_cortes(barbeiro_id, mes, ano)
    total_bruto = sum(c["valor"] for c in cortes)
    comissao = total_bruto * COMISSAO_PERCENTUAL

    servicos_count = {}
    for c in cortes:
        nome = c["servico_nome"]
        servicos_count[nome] = servicos_count.get(nome, 0) + 1

    return {
        "mes": mes,
        "ano": ano,
        "total_cortes": len(cortes),
        "total_bruto": total_bruto,
        "comissao": comissao,
        "percentual": COMISSAO_PERCENTUAL * 100,
        "cortes": cortes,
        "servicos_populares": sorted(servicos_count.items(), key=lambda x: x[1], reverse=True)[:5],
    }


def deletar_corte(corte_id: int, barbeiro_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cortes WHERE id = ? AND barbeiro_id = ?", (corte_id, barbeiro_id))
    afetado = cur.rowcount > 0
    conn.commit()
    conn.close()
    return afetado
