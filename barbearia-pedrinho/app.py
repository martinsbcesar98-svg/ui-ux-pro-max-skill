from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from database.db import (
    inicializar_db, autenticar, registrar_corte,
    obter_cortes, calcular_resumo_mensal, deletar_corte, SERVICOS
)

app = Flask(__name__)
app.secret_key = "pedrinho_barbearia_secret_2025"

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "barbeiro" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/", methods=["GET", "POST"])
def login():
    if "barbeiro" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        senha = request.form.get("senha", "").strip()
        barbeiro = autenticar(username, senha)
        if barbeiro:
            session["barbeiro"] = barbeiro
            flash(f"Bem-vindo, {barbeiro['nome']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Utilizador ou senha incorretos.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    barbeiro = session["barbeiro"]
    hoje = datetime.today()
    mes = int(request.args.get("mes", hoje.month))
    ano = int(request.args.get("ano", hoje.year))

    resumo = calcular_resumo_mensal(barbeiro["id"], mes, ano)
    cortes_hoje = obter_cortes(barbeiro["id"], hoje.month, hoje.year)
    cortes_hoje = [c for c in cortes_hoje if c["data"] == hoje.strftime("%Y-%m-%d")]

    anos_disponiveis = list(range(hoje.year - 2, hoje.year + 1))

    return render_template("dashboard.html",
        barbeiro=barbeiro,
        resumo=resumo,
        cortes_hoje=cortes_hoje,
        mes_nome=MESES_PT[mes],
        mes_atual=mes,
        ano_atual=ano,
        meses=MESES_PT,
        anos=anos_disponiveis,
        hoje=hoje.strftime("%Y-%m-%d"),
        servicos=SERVICOS,
    )


@app.route("/registrar", methods=["GET", "POST"])
@login_required
def registrar():
    barbeiro = session["barbeiro"]

    if request.method == "POST":
        data = request.form.get("data", "").strip()
        servico_key = request.form.get("servico_key", "").strip()
        valor_str = request.form.get("valor", "").strip().replace(",", ".")
        observacao = request.form.get("observacao", "").strip()

        erros = []
        if not data:
            erros.append("Data é obrigatória.")
        if servico_key not in SERVICOS:
            erros.append("Serviço inválido.")
        try:
            valor = float(valor_str)
            if valor <= 0:
                raise ValueError
        except ValueError:
            erros.append("Valor inválido.")

        if erros:
            for e in erros:
                flash(e, "error")
        else:
            registrar_corte(barbeiro["id"], data, servico_key, valor, observacao)
            flash("Corte registado com sucesso!", "success")
            return redirect(url_for("dashboard"))

    hoje = datetime.today().strftime("%Y-%m-%d")
    return render_template("registrar.html",
        barbeiro=barbeiro,
        servicos=SERVICOS,
        hoje=hoje,
    )


@app.route("/historico")
@login_required
def historico():
    barbeiro = session["barbeiro"]
    hoje = datetime.today()
    mes = int(request.args.get("mes", hoje.month))
    ano = int(request.args.get("ano", hoje.year))

    cortes = obter_cortes(barbeiro["id"], mes, ano)
    resumo = calcular_resumo_mensal(barbeiro["id"], mes, ano)
    anos_disponiveis = list(range(hoje.year - 2, hoje.year + 1))

    return render_template("historico.html",
        barbeiro=barbeiro,
        cortes=cortes,
        resumo=resumo,
        mes_nome=MESES_PT[mes],
        mes_atual=mes,
        ano_atual=ano,
        meses=MESES_PT,
        anos=anos_disponiveis,
    )


@app.route("/deletar/<int:corte_id>", methods=["POST"])
@login_required
def deletar(corte_id):
    barbeiro = session["barbeiro"]
    sucesso = deletar_corte(corte_id, barbeiro["id"])
    if sucesso:
        flash("Registo eliminado.", "success")
    else:
        flash("Erro ao eliminar registo.", "error")
    return redirect(request.referrer or url_for("historico"))


@app.route("/api/preco/<servico_key>")
@login_required
def api_preco(servico_key):
    servico = SERVICOS.get(servico_key)
    if servico:
        return jsonify({"preco": servico["preco"]})
    return jsonify({"preco": 0}), 404


if __name__ == "__main__":
    inicializar_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
