from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import mysql.connector
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from emails import correr_todos  # <-- IMPORTAÇÃO PARA OS EMAILS

app = Flask(__name__)
app.secret_key = "inkmanager_secret"

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "QwertyuioP@1706",
    "database": "inkmanager"
}

UPLOAD_FOLDER   = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def conectar():
    return mysql.connector.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─────────────────────────────────────────────
#  SERVIR FICHEIROS UPLOADED
# ─────────────────────────────────────────────
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ─────────────────────────────────────────────
#  DASHBOARD E EMAILS
# ─────────────────────────────────────────────
@app.route("/")
def dashboard():
    conn = conectar(); cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total FROM clientes")
    total_clientes = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM marcacoes")
    total_marcacoes = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM marcacoes WHERE estado='Pendente'")
    pendentes = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM marcacoes WHERE estado='Concluída'")
    concluidas = cur.fetchone()["total"]

    cur.execute('''
        SELECT m.id, m.id_cliente, c.nome, m.data_hora, m.tipo, m.descricao, m.valor, m.estado
        FROM marcacoes m JOIN clientes c ON m.id_cliente=c.id
        WHERE m.data_hora >= NOW() AND m.estado='Pendente'
        ORDER BY m.data_hora ASC LIMIT 5
    ''')
    proximas = cur.fetchall()

    cur.execute("SELECT id, nome, telemovel, instagram, data_registo FROM clientes ORDER BY data_registo DESC LIMIT 5")
    recentes = cur.fetchall()

    cur.close(); conn.close()
    return render_template("dashboard.html",
        total_clientes=total_clientes, total_marcacoes=total_marcacoes,
        pendentes=pendentes, concluidas=concluidas,
        proximas=proximas, recentes=recentes)

@app.route("/disparar_emails", methods=["POST"])
def disparar_emails():
    try:
        correr_todos()
        flash("📧 Emails automáticos verificados e processados com sucesso!", "sucesso")
    except Exception as e:
        flash(f"Erro ao processar emails: {e}", "erro")
    return redirect(url_for("dashboard"))

# ─────────────────────────────────────────────
#  CLIENTES
# ─────────────────────────────────────────────
@app.route("/clientes")
def clientes():
    pesquisa = request.args.get("q", "").strip()
    conn = conectar(); cur = conn.cursor(dictionary=True)
    if pesquisa:
        cur.execute('''SELECT id, nome, telemovel, instagram, email, data_registo
            FROM clientes WHERE nome LIKE %s OR telemovel LIKE %s OR instagram LIKE %s
            ORDER BY nome''', (f"%{pesquisa}%", f"%{pesquisa}%", f"%{pesquisa}%"))
    else:
        cur.execute("SELECT id, nome, telemovel, instagram, email, data_registo FROM clientes ORDER BY nome")
    lista = cur.fetchall()
    cur.close(); conn.close()
    return render_template("clientes.html", clientes=lista, pesquisa=pesquisa)

@app.route("/clientes/novo", methods=["GET","POST"])
def novo_cliente():
    if request.method == "POST":
        nome   = request.form.get("nome","").strip()
        data_n = request.form.get("data_nascimento") or None
        tel    = request.form.get("telemovel") or None
        insta  = request.form.get("instagram") or None
        email  = request.form.get("email") or None
        obs    = request.form.get("observacoes") or None
        if not nome:
            flash("O nome é obrigatório.", "erro")
            return render_template("form_cliente.html", cliente=request.form, titulo="Novo Cliente")
        try:
            conn = conectar(); cur = conn.cursor()
            cur.execute('''INSERT INTO clientes (nome,data_nascimento,telemovel,instagram,email,observacoes)
                VALUES (%s,%s,%s,%s,%s,%s)''',(nome,data_n,tel,insta,email,obs))
            conn.commit()
            flash(f"Cliente '{nome}' adicionado!", "sucesso")
            cur.close(); conn.close()
            return redirect(url_for("clientes"))
        except Exception as e:
            flash(f"Erro: {e}", "erro")
    return render_template("form_cliente.html", cliente={}, titulo="Novo Cliente")

@app.route("/clientes/<int:id_c>")
def ficha_cliente(id_c):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM clientes WHERE id=%s", (id_c,))
    cliente = cur.fetchone()
    if not cliente:
        flash("Cliente não encontrado.", "erro")
        return redirect(url_for("clientes"))
    cur.execute("SELECT * FROM marcacoes WHERE id_cliente=%s ORDER BY data_hora DESC", (id_c,))
    marcacoes = cur.fetchall()
    cur.execute("SELECT * FROM ficheiros WHERE id_cliente=%s ORDER BY data_upload DESC", (id_c,))
    ficheiros = cur.fetchall()
    cur.close(); conn.close()
    return render_template("ficha.html", cliente=cliente, marcacoes=marcacoes, ficheiros=ficheiros)

@app.route("/clientes/<int:id_c>/editar", methods=["GET","POST"])
def editar_cliente(id_c):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM clientes WHERE id=%s", (id_c,))
    cliente = cur.fetchone()
    if not cliente:
        flash("Cliente não encontrado.", "erro")
        return redirect(url_for("clientes"))
    if request.method == "POST":
        nome   = request.form.get("nome","").strip()
        data_n = request.form.get("data_nascimento") or None
        tel    = request.form.get("telemovel") or None
        insta  = request.form.get("instagram") or None
        email  = request.form.get("email") or None
        obs    = request.form.get("observacoes") or None
        if not nome:
            flash("O nome é obrigatório.", "erro")
        else:
            try:
                cur2 = conn.cursor()
                cur2.execute('''UPDATE clientes SET nome=%s,data_nascimento=%s,telemovel=%s,
                    instagram=%s,email=%s,observacoes=%s WHERE id=%s''',
                    (nome,data_n,tel,insta,email,obs,id_c))
                conn.commit(); cur2.close()
                flash("Cliente atualizado!", "sucesso")
                cur.close(); conn.close()
                return redirect(url_for("ficha_cliente", id_c=id_c))
            except Exception as e:
                flash(f"Erro: {e}", "erro")
    cur.close(); conn.close()
    return render_template("form_cliente.html", cliente=cliente, titulo="Editar Cliente")

@app.route("/clientes/<int:id_c>/apagar", methods=["POST"])
def apagar_cliente(id_c):
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT caminho FROM ficheiros WHERE id_cliente=%s", (id_c,))
        for row in cur.fetchall():
            if os.path.exists(row[0]): os.remove(row[0])
        cur.execute("DELETE FROM clientes WHERE id=%s", (id_c,))
        conn.commit(); cur.close(); conn.close()
        flash("Cliente apagado.", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("clientes"))

# ─────────────────────────────────────────────
#  FICHEIROS
# ─────────────────────────────────────────────
@app.route("/clientes/<int:id_c>/upload", methods=["POST"])
def upload_ficheiro(id_c):
    descricao  = request.form.get("descricao") or None
    id_marcacao = request.form.get("id_marcacao") or None

    if 'ficheiro' not in request.files:
        flash("Nenhum ficheiro selecionado.", "erro")
        return redirect(url_for("ficha_cliente", id_c=id_c))

    f = request.files['ficheiro']
    if f.filename == '':
        flash("Nenhum ficheiro selecionado.", "erro")
        return redirect(url_for("ficha_cliente", id_c=id_c))

    if not allowed_file(f.filename):
        flash("Tipo de ficheiro não suportado. Usa JPG, PNG, PDF ou TXT.", "erro")
        return redirect(url_for("ficha_cliente", id_c=id_c))

    ext          = f.filename.rsplit('.', 1)[1].lower()
    nome_orig    = secure_filename(f.filename)
    ts           = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_guardado = f"cli{id_c}_{ts}_{nome_orig}"
    caminho      = os.path.join(UPLOAD_FOLDER, nome_guardado)
    f.save(caminho)

    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute('''INSERT INTO ficheiros (id_cliente, id_marcacao, nome_ficheiro, tipo, caminho, descricao)
            VALUES (%s, %s, %s, %s, %s, %s)''',
            (id_c, id_marcacao or None, nome_orig, ext, caminho, descricao))
        conn.commit()
        flash(f"Ficheiro '{nome_orig}' carregado com sucesso!", "sucesso")
        cur.close(); conn.close()
    except Exception as e:
        try:
            conn2 = conectar(); cur2 = conn2.cursor()
            cur2.execute('''INSERT INTO ficheiros (id_cliente, nome_ficheiro, tipo, caminho, descricao)
                VALUES (%s, %s, %s, %s, %s)''',
                (id_c, nome_orig, ext, caminho, descricao))
            conn2.commit()
            flash(f"Ficheiro '{nome_orig}' carregado!", "sucesso")
            cur2.close(); conn2.close()
        except Exception as e2:
            flash(f"Erro: {e2}", "erro")
    return redirect(url_for("ficha_cliente", id_c=id_c))

@app.route("/ficheiros/<int:id_f>/apagar", methods=["POST"])
def apagar_ficheiro(id_f):
    id_c = request.form.get("id_cliente")
    try:
        conn = conectar(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT caminho, nome_ficheiro FROM ficheiros WHERE id=%s", (id_f,))
        row = cur.fetchone()
        if row:
            if os.path.exists(row['caminho']): os.remove(row['caminho'])
            cur2 = conn.cursor()
            cur2.execute("DELETE FROM ficheiros WHERE id=%s", (id_f,))
            conn.commit(); cur2.close()
            flash(f"Ficheiro '{row['nome_ficheiro']}' apagado.", "sucesso")
        cur.close(); conn.close()
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(url_for("ficha_cliente", id_c=id_c))

@app.route("/ficheiros/<int:id_f>/ver")
def ver_ficheiro(id_f):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ficheiros WHERE id=%s", (id_f,))
    f = cur.fetchone()
    cur.close(); conn.close()
    if not f:
        flash("Ficheiro não encontrado.", "erro")
        return redirect(url_for("clientes"))
    nome_guardado = os.path.basename(f['caminho'])
    return send_from_directory(UPLOAD_FOLDER, nome_guardado)

# ─────────────────────────────────────────────
#  MARCAÇÕES
# ─────────────────────────────────────────────
@app.route("/marcacoes")
def marcacoes():
    estado = request.args.get("estado", "")
    conn = conectar(); cur = conn.cursor(dictionary=True)
    if estado:
        cur.execute('''SELECT m.*, c.nome as nome_cliente FROM marcacoes m
            JOIN clientes c ON m.id_cliente=c.id
            WHERE m.estado=%s ORDER BY m.data_hora ASC''', (estado,))
    else:
        cur.execute('''SELECT m.*, c.nome as nome_cliente FROM marcacoes m
            JOIN clientes c ON m.id_cliente=c.id ORDER BY m.data_hora ASC''')
    lista = cur.fetchall()
    cur.close(); conn.close()
    return render_template("marcacoes.html", marcacoes=lista, estado_filtro=estado)

@app.route("/marcacoes/nova", methods=["GET","POST"])
def nova_marcacao():
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes_lista = cur.fetchall()

    if request.method == "POST":
        id_c      = request.form.get("id_cliente")
        data_hora = request.form.get("data_hora")
        tipo      = request.form.get("tipo","Tatuagem")
        descricao = request.form.get("descricao") or None
        valor     = request.form.get("valor") or None
        materiais = request.form.get("materiais") or None
        duracao   = request.form.get("duracao") or None
        notas     = request.form.get("notas") or None
        if not id_c or not data_hora:
            flash("Cliente e data/hora são obrigatórios.", "erro")
        else:
            try:
                if valor: valor = float(valor)
                cur2 = conn.cursor()
                cur2.execute('''INSERT INTO marcacoes
                    (id_cliente,data_hora,tipo,descricao,valor,materiais,duracao,estado,notas)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,'Pendente',%s)''',
                    (id_c,data_hora,tipo,descricao,valor,materiais,duracao,notas))
                conn.commit(); cur2.close()
                flash("Marcação adicionada!", "sucesso")
                cur.close(); conn.close()
                return redirect(url_for("marcacoes"))
            except Exception as e:
                flash(f"Erro: {e}", "erro")

    cur.close(); conn.close()
    return render_template("form_marcacao.html", clientes=clientes_lista, marcacao={}, titulo="Nova Marcação")

@app.route("/marcacoes/<int:id_m>/editar", methods=["GET", "POST"])
def editar_marcacao(id_m):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes_lista = cur.fetchall()

    cur.execute("SELECT * FROM marcacoes WHERE id=%s", (id_m,))
    marcacao = cur.fetchone()

    if not marcacao:
        flash("Marcação não encontrada.", "erro")
        cur.close(); conn.close()
        return redirect(url_for("marcacoes"))

    if request.method == "POST":
        id_c      = request.form.get("id_cliente")
        data_hora = request.form.get("data_hora")
        tipo      = request.form.get("tipo", "Tatuagem")
        descricao = request.form.get("descricao") or None
        valor     = request.form.get("valor") or None
        materiais = request.form.get("materiais") or None
        duracao   = request.form.get("duracao") or None
        notas     = request.form.get("notas") or None

        if not id_c or not data_hora:
            flash("Cliente e data/hora são obrigatórios.", "erro")
        else:
            try:
                if valor: valor = float(valor)
                cur2 = conn.cursor()
                cur2.execute('''UPDATE marcacoes SET 
                    id_cliente=%s, data_hora=%s, tipo=%s, descricao=%s, 
                    valor=%s, materiais=%s, duracao=%s, notas=%s 
                    WHERE id=%s''',
                    (id_c, data_hora, tipo, descricao, valor, materiais, duracao, notas, id_m))
                conn.commit(); cur2.close()
                flash("Marcação atualizada com sucesso!", "sucesso")
                cur.close(); conn.close()
                return redirect(url_for("marcacoes"))
            except Exception as e:
                flash(f"Erro ao atualizar: {e}", "erro")

    cur.close(); conn.close()
    
    # Formata a data para preencher o formulário
    if marcacao['data_hora']:
        marcacao['data_hora'] = marcacao['data_hora'].strftime('%Y-%m-%dT%H:%M')

    return render_template("form_marcacao.html", clientes=clientes_lista, marcacao=marcacao, titulo="Editar Marcação")

@app.route("/marcacoes/<int:id_m>/estado", methods=["POST"])
def alterar_estado(id_m):
    estado = request.form.get("estado")
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute("UPDATE marcacoes SET estado=%s WHERE id=%s", (estado, id_m))
        conn.commit(); cur.close(); conn.close()
        flash(f"Estado alterado para '{estado}'!", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(request.referrer or url_for("marcacoes"))

@app.route("/marcacoes/<int:id_m>/apagar", methods=["POST"])
def apagar_marcacao(id_m):
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute("DELETE FROM marcacoes WHERE id=%s", (id_m,))
        conn.commit(); cur.close(); conn.close()
        flash("Marcação apagada.", "sucesso")
    except Exception as e:
        flash(f"Erro: {e}", "erro")
    return redirect(request.referrer or url_for("marcacoes"))

if __name__ == "__main__":
    app.run(debug=True)