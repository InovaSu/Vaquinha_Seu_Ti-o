from flask import Flask, request, redirect, url_for, render_template_string, session, flash
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "troque_esta_chave_por_uma_bem_segura_essa_parece_ser_segura1289@%$."

DATA_FILE = "dados_vaquinha.json"
ADMIN_PASSWORD = ".Elefante.77"


def parse_moeda_brasileira(valor):
    valor = str(valor).strip()
    if not valor:
        return 0.0

    valor = valor.replace("R$", "").replace(" ", "")

    if "," in valor and "." in valor:
        valor = valor.replace(".", "").replace(",", ".")
    elif "," in valor:
        valor = valor.replace(",", ".")

    return float(valor)


def formatar_moeda_brl(valor):
    return "{:,.2f}".format(float(valor)).replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_dados():
    if not os.path.exists(DATA_FILE):
        dados_iniciais = {
            "titulo": "Vaquinha solidária",
            "descricao": "Olá! Meu nome é Suellen Almeida e esta vaquinha foi criada para ajudar meu pai, mais conhecido como Seu Tião, que tem HBP (hiperplasia benigna da próstata) e precisará fazer uma cirurgia com urgência no mês de maio, assim que concluir a recuperação da anemia que desenvolveu após perder muito sangue recentemente. Estamos arrecadando ajuda para cobrir o procedimento RTU/Prostatectomia Simples, orçado em R$ 15.000,00 pelo urologista que vem acompanhando o caso dele. Qualquer valor faz diferença. Agradeço pelas orações e peço que continuem compartilhando o link da vaquinha. Deus abençoe!",
            "meta": 15000.0,
            "arrecadado": 0.0,
            "pix": "31971122325",
            "mensagem": "Toda ajuda faz diferença. Muito obrigada!"
        }
        salvar_dados(dados_iniciais)
        return dados_iniciais

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logado"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


PUBLIC_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ dados.titulo }}</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: #0d0d0d;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 24px;
        }
        .card {
            width: 100%;
            max-width: 720px;
            background: #161616;
            border: 1px solid #2b2b2b;
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        }
        h1 {
            margin-top: 0;
            font-size: 2rem;
            text-align: center;
        }
        p {
            line-height: 1.6;
            color: #d8d8d8;
        }
        .valor {
            font-size: 2.2rem;
            font-weight: bold;
            text-align: center;
            margin: 20px 0 8px;
        }
        .meta {
            text-align: center;
            color: #bdbdbd;
            margin-bottom: 20px;
        }
        .barra {
            width: 100%;
            height: 18px;
            background: #2a2a2a;
            border-radius: 999px;
            overflow: hidden;
            margin-bottom: 24px;
        }
        .progresso {
            height: 100%;
            width: {{ progresso }}%;
            background: linear-gradient(90deg, #7c3aed, #22c55e);
            border-radius: 999px;
            transition: width 0.4s ease;
        }
        .pix-box {
            background: #101010;
            border: 1px dashed #4b4b4b;
            padding: 16px;
            border-radius: 14px;
            margin-top: 20px;
        }
        .pix-label {
            font-size: 0.95rem;
            color: #aaaaaa;
            margin-bottom: 8px;
        }
        .pix-chave {
            font-size: 1.05rem;
            word-break: break-word;
            color: #ffffff;
        }
        .rodape {
            margin-top: 22px;
            text-align: center;
            color: #8d8d8d;
            font-size: 0.95rem;
        }
        .botao {
            margin-top: 14px;
            display: inline-block;
            background: #ffffff;
            color: #111111;
            text-decoration: none;
            padding: 12px 18px;
            border-radius: 12px;
            font-weight: bold;
        }
        .center { text-align: center; }
    </style>
</head>
<body>
    <div class="card">
        <h1>{{ dados.titulo }}</h1>
        <p>{{ dados.descricao }}</p>

        <div class="valor">R$ {{ formatar_moeda_brl(dados.arrecadado) }}</div>
        <div class="meta">Meta: R$ {{ formatar_moeda_brl(dados.meta) }}</div>

        <div class="barra">
            <div class="progresso"></div>
        </div>

        <p>{{ dados.mensagem }}</p>

        <div class="pix-box">
            <div class="pix-label">Chave Pix para contribuir</div>
            <div class="pix-chave">{{ dados.pix }}</div>
        </div>

        <div class="rodape">Você também pode ajudar compartilhando esta página.</div>
    </div>
</body>
</html>
"""


LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Admin</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .box {
            width: 100%;
            max-width: 380px;
            background: #1a1a1a;
            padding: 24px;
            border-radius: 18px;
            border: 1px solid #333;
        }
        input, button {
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            border-radius: 10px;
            border: 1px solid #444;
            font-size: 1rem;
        }
        input { background: #0f0f0f; color: white; }
        button { background: white; color: black; font-weight: bold; cursor: pointer; }
        .flash { color: #ff8a8a; margin-top: 12px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Área administrativa</h2>
        <form method="post">
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Entrar</button>
        </form>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="flash">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}
    </div>
</body>
</html>
"""


ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin - Vaquinha</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            margin: 0;
            padding: 24px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #1a1a1a;
            padding: 24px;
            border-radius: 18px;
            border: 1px solid #333;
        }
        h1 { margin-top: 0; }
        label {
            display: block;
            margin-top: 14px;
            margin-bottom: 6px;
        }
        input, textarea, button {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #444;
            font-size: 1rem;
            background: #0f0f0f;
            color: white;
        }
        textarea { min-height: 100px; resize: vertical; }
        button {
            background: white;
            color: black;
            font-weight: bold;
            cursor: pointer;
            margin-top: 18px;
        }
        a {
            color: #c9c9c9;
            text-decoration: none;
        }
        .topo {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }
        .flash { color: #90ee90; margin-top: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="topo">
            <h1>Painel da vaquinha</h1>
            <div>
                <a href="/" target="_blank">Ver página pública</a> |
                <a href="/logout">Sair</a>
            </div>
        </div>

        <form method="post">
            <label>Título</label>
            <input type="text" name="titulo" value="{{ dados.titulo }}" required>

            <label>Descrição</label>
            <textarea name="descricao" required>{{ dados.descricao }}</textarea>

            <label>Meta</label>
            <input type="text" name="meta" value="{{ formatar_moeda_brl(dados.meta) }}" required>

            <label>Valor arrecadado</label>
            <input type="text" name="arrecadado" value="{{ formatar_moeda_brl(dados.arrecadado) }}" required>

            <label>Chave Pix</label>
            <input type="text" name="pix" value="{{ dados.pix }}" required>

            <label>Mensagem</label>
            <textarea name="mensagem" required>{{ dados.mensagem }}</textarea>

            <button type="submit">Salvar alterações</button>
        </form>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="flash">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}
    </div>
</body>
</html>
"""


@app.route("/")
def pagina_publica():
    dados = carregar_dados()
    meta = float(dados.get("meta", 0))
    arrecadado = float(dados.get("arrecadado", 0))
    progresso = 0 if meta <= 0 else min((arrecadado / meta) * 100, 100)
    return render_template_string(
        PUBLIC_TEMPLATE,
        dados=dados,
        progresso=progresso,
        formatar_moeda_brl=formatar_moeda_brl
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        senha = request.form.get("senha", "")
        if senha == ADMIN_PASSWORD:
            session["admin_logado"] = True
            return redirect(url_for("admin"))
        flash("Senha incorreta.")
    return render_template_string(LOGIN_TEMPLATE)


@app.route("/logout")
def logout():
    session.pop("admin_logado", None)
    return redirect(url_for("login"))


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    dados = carregar_dados()

    if request.method == "POST":
        dados["titulo"] = request.form.get("titulo", "").strip()
        dados["descricao"] = request.form.get("descricao", "").strip()
        dados["meta"] = parse_moeda_brasileira(request.form.get("meta", 0))
        dados["arrecadado"] = parse_moeda_brasileira(request.form.get("arrecadado", 0))
        dados["pix"] = request.form.get("pix", "").strip()
        dados["mensagem"] = request.form.get("mensagem", "").strip()
        salvar_dados(dados)
        flash("Alterações salvas com sucesso.")
        return redirect(url_for("admin"))

    return render_template_string(
        ADMIN_TEMPLATE,
        dados=dados,
        formatar_moeda_brl=formatar_moeda_brl
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
