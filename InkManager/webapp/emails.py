import smtplib
import mysql.connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, date

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES
# ─────────────────────────────────────────────
EMAIL_REMETENTE = "nusaaink@gmail.com"
EMAIL_PASSWORD  = "nimzqwhosguacxol"
NOME_STUDIO     = "NusaaInk"

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "QwertyuioP@1706",
    "database": "inkmanager"
}

# ─────────────────────────────────────────────
#  ENVIAR EMAIL
# ─────────────────────────────────────────────
def enviar_email(destinatario, assunto, corpo_html):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"]    = f"{NOME_STUDIO} <{EMAIL_REMETENTE}>"
        msg["To"]      = destinatario

        msg.attach(MIMEText(corpo_html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_REMETENTE, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())

        print(f"  ✅ Email enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"  ❌ Erro ao enviar para {destinatario}: {e}")
        return False


def conectar():
    return mysql.connector.connect(**DB_CONFIG)


# ─────────────────────────────────────────────
#  TEMPLATES DE EMAIL
# ─────────────────────────────────────────────
def template_base(conteudo, titulo):
    return f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head><meta charset="UTF-8">
    <style>
        body {{ font-family: 'Georgia', serif; background: #f5e6c8; margin: 0; padding: 0; }}
        .wrapper {{ max-width: 580px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(43,45,47,0.12); }}
        .header {{ background: #2b2d2f; padding: 36px 40px; text-align: center; }}
        .header h1 {{ font-family: 'Georgia', serif; color: #f5e6c8; font-size: 1.6rem; margin: 0; letter-spacing: 2px; }}
        .header p {{ color: #a68d44; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; margin: 8px 0 0; }}
        .body {{ padding: 40px; color: #2b2d2f; line-height: 1.8; }}
        .body h2 {{ font-family: 'Georgia', serif; font-size: 1.4rem; color: #2b2d2f; margin-bottom: 16px; }}
        .body p {{ font-size: 0.95rem; margin-bottom: 14px; color: #3d4042; }}
        .highlight {{ background: #f5e6c8; border-left: 4px solid #a68d44; padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 24px 0; }}
        .highlight p {{ margin: 0; font-size: 0.9rem; }}
        .badge {{ display: inline-block; background: #a68d44; color: white; padding: 8px 24px; border-radius: 24px; font-size: 0.85rem; font-weight: bold; letter-spacing: 1px; margin: 8px 0; }}
        .list {{ padding-left: 20px; }}
        .list li {{ font-size: 0.9rem; color: #3d4042; margin-bottom: 8px; }}
        .footer {{ background: #2b2d2f; padding: 24px 40px; text-align: center; }}
        .footer p {{ color: #9a8da2; font-size: 0.75rem; margin: 0; letter-spacing: 0.5px; }}
        .footer a {{ color: #a68d44; text-decoration: none; }}
    </style>
    </head>
    <body>
    <div class="wrapper">
        <div class="header">
            <h1>💉 {NOME_STUDIO}</h1>
            <p>{titulo}</p>
        </div>
        <div class="body">
            {conteudo}
        </div>
        <div class="footer">
            <p>© 2026 {NOME_STUDIO} · <a href="mailto:{EMAIL_REMETENTE}">{EMAIL_REMETENTE}</a></p>
        </div>
    </div>
    </body>
    </html>
    """


def email_aniversario(nome):
    conteudo = f"""
        <h2>Feliz Aniversário, {nome}! 🎂</h2>
        <p>Hoje é o teu dia especial e nós não podíamos deixar passar em branco!</p>
        <p>Como forma de celebrar contigo, temos um presente especial:</p>
        <div class="highlight">
            <p style="text-align:center; font-size:1.1rem; font-weight:bold; color:#a68d44;">
                🎁 10% de desconto em qualquer sessão<br>
                <span style="font-size:0.85rem; color:#5a5c5e;">válido durante todo o mês do teu aniversário</span>
            </p>
        </div>
        <p>Basta mencionares este email quando agendares a tua próxima sessão.</p>
        <p>Que este ano seja tão incrível quanto a tua arte! ✨</p>
        <p>Com carinho,<br><strong>Equipa {NOME_STUDIO}</strong></p>
    """
    return template_base(conteudo, "Feliz Aniversário")


def email_pre_tattoo(nome, data_marcacao, descricao):
    data_fmt = data_marcacao.strftime('%d/%m/%Y às %H:%M') if hasattr(data_marcacao, 'strftime') else str(data_marcacao)
    conteudo = f"""
        <h2>Está quase na hora! 🖊️</h2>
        <p>Olá <strong>{nome}</strong>! A tua sessão está a aproximar-se:</p>
        <div class="highlight">
            <p><strong>📅 Data:</strong> {data_fmt}<br>
            <strong>🖊️ Sessão:</strong> {descricao or 'Tatuagem'}</p>
        </div>
        <p><strong>Para garantires o melhor resultado, segue estes cuidados nos dias anteriores:</strong></p>
        <ul class="list">
            <li>💧 <strong>Hidrata bem a pele</strong> — aplica creme hidratante na zona a tatuar durante os dias anteriores</li>
            <li>🚫 <strong>Evita álcool</strong> nas 24h antes da sessão</li>
            <li>😴 <strong>Dorme bem</strong> na noite anterior</li>
            <li>🍽️ <strong>Come uma refeição completa</strong> antes de vires — nunca venhas em jejum</li>
            <li>🧴 <strong>Não uses cremes, óleos ou autobronzeador</strong> no dia da sessão</li>
            <li>👕 <strong>Veste roupa confortável</strong> que permita acesso fácil à zona a tatuar</li>
            <li>☀️ <strong>Evita exposição solar excessiva</strong> na zona a tatuar</li>
        </ul>
        <p>Qualquer dúvida, não hesites em contactar-nos. Estamos à espera de te receber! 🤩</p>
        <p>Até breve,<br><strong>Equipa {NOME_STUDIO}</strong></p>
    """
    return template_base(conteudo, "Cuidados Pré-Tattoo")


def email_pos_tattoo(nome, descricao):
    conteudo = f"""
        <h2>A tua nova tatuagem precisa de ti! 🩹</h2>
        <p>Olá <strong>{nome}</strong>! Que sessão incrível — obrigada pela confiança!</p>
        <p>Para garantires que a tua <strong>{descricao or 'tatuagem'}</strong> cura na perfeição, segue estes cuidados:</p>
        <ul class="list">
            <li>🧻 <strong>Remove o film/penso</strong> após 2-4 horas (ou conforme indicado)</li>
            <li>🧼 <strong>Lava suavemente</strong> com água morna e sabão neutro, sem esfregar</li>
            <li>💧 <strong>Seca com pequenas pancadinhas</strong> — nunca esfregues</li>
            <li>🧴 <strong>Aplica creme cicatrizante</strong> (Bepanthene ou similar) 2-3x por dia em camada fina</li>
            <li>☀️ <strong>Protege do sol</strong> — sem exposição solar direta durante a cicatrização</li>
            <li>🏊 <strong>Evita piscina, mar e banhos de banheira</strong> durante 2-3 semanas</li>
            <li>🚫 <strong>Não arranques as películas</strong> — deixa cair naturalmente</li>
            <li>👕 <strong>Usa roupa folgada</strong> sobre a tatuagem</li>
        </ul>
        <div class="highlight">
            <p>⚠️ <strong>Atenção:</strong> Se notares vermidão excessiva, inchaço, pus ou febre, contacta-nos imediatamente ou consulta um médico.</p>
        </div>
        <p>A cicatrização completa demora entre 2 a 4 semanas. Estamos aqui para qualquer dúvida! 💜</p>
        <p>Com carinho,<br><strong>Equipa {NOME_STUDIO}</strong></p>
    """
    return template_base(conteudo, "Cuidados Pós-Tattoo")


def email_foto_followup(nome, descricao):
    conteudo = f"""
        <h2>Como está a tua tatuagem? 📸</h2>
        <p>Olá <strong>{nome}</strong>! Já passaram duas semanas desde a tua sessão de <strong>{descricao or 'tatuagem'}</strong>.</p>
        <p>Nesta fase a cicatrização já deve estar bastante avançada — adorávamos ver como está a ficar! 🤩</p>
        <div class="highlight">
            <p>📸 <strong>Tira uma foto e envia-nos!</strong><br>
            Podes responder diretamente a este email ou marcar-nos no Instagram.<br>
            O teu feedback é muito importante para nós.</p>
        </div>
        <p>Se tiveres alguma dúvida sobre a cicatrização ou quiseres agendar um <strong>retoque gratuito</strong>, é só entrar em contacto!</p>
        <p>Obrigada pela confiança,<br><strong>Equipa {NOME_STUDIO}</strong></p>
    """
    return template_base(conteudo, "Follow-up 2 Semanas")


# ─────────────────────────────────────────────
#  LÓGICA DE AUTOMAÇÃO
# ─────────────────────────────────────────────
def verificar_aniversarios():
    """Envia email a clientes que fazem anos hoje."""
    print("\n📅 A verificar aniversários...")
    hoje = date.today()
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT nome, email, data_nascimento FROM clientes
        WHERE email IS NOT NULL AND email != ''
        AND DAY(data_nascimento) = %s AND MONTH(data_nascimento) = %s
    """, (hoje.day, hoje.month))
    clientes = cur.fetchall()
    cur.close(); conn.close()

    for c in clientes:
        print(f"  🎂 Aniversário: {c['nome']}")
        html = email_aniversario(c['nome'])
        enviar_email(c['email'], f"🎂 Feliz Aniversário, {c['nome']}! Presente especial para ti 🎁", html)

    if not clientes:
        print("  (Nenhum aniversário hoje)")


def verificar_pre_tattoo():
    """Envia email 3 dias antes de marcações de tatuagem."""
    print("\n🖊️  A verificar marcações nos próximos 3 dias...")
    alvo = date.today() + timedelta(days=3)
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.nome, c.email, m.data_hora, m.descricao, m.id
        FROM marcacoes m JOIN clientes c ON m.id_cliente = c.id
        WHERE c.email IS NOT NULL AND c.email != ''
        AND DATE(m.data_hora) = %s
        AND m.tipo = 'Tatuagem'
        AND m.estado = 'Pendente'
    """, (alvo,))
    marcacoes = cur.fetchall()
    cur.close(); conn.close()

    for m in marcacoes:
        print(f"  📋 Pré-tattoo: {m['nome']} — {m['data_hora']}")
        html = email_pre_tattoo(m['nome'], m['data_hora'], m['descricao'])
        enviar_email(m['email'], f"📋 A tua sessão é daqui a 3 dias — cuidados importantes!", html)

    if not marcacoes:
        print("  (Nenhuma marcação daqui a 3 dias)")


def verificar_pos_tattoo():
    """Envia email a clientes com marcações concluídas hoje."""
    print("\n🩹 A verificar marcações concluídas hoje...")
    hoje = date.today()
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.nome, c.email, m.descricao, m.id
        FROM marcacoes m JOIN clientes c ON m.id_cliente = c.id
        WHERE c.email IS NOT NULL AND c.email != ''
        AND DATE(m.data_hora) = %s
        AND m.tipo = 'Tatuagem'
        AND m.estado = 'Concluída'
    """, (hoje,))
    marcacoes = cur.fetchall()
    cur.close(); conn.close()

    for m in marcacoes:
        print(f"  🩹 Pós-tattoo: {m['nome']}")
        html = email_pos_tattoo(m['nome'], m['descricao'])
        enviar_email(m['email'], f"🩹 Cuidados pós-tattoo — informação importante", html)

    if not marcacoes:
        print("  (Nenhuma marcação concluída hoje)")


def verificar_followup():
    """Envia email 14 dias após marcação concluída."""
    print("\n📸 A verificar follow-ups (2 semanas)...")
    alvo = date.today() - timedelta(days=14)
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.nome, c.email, m.descricao, m.id
        FROM marcacoes m JOIN clientes c ON m.id_cliente = c.id
        WHERE c.email IS NOT NULL AND c.email != ''
        AND DATE(m.data_hora) = %s
        AND m.tipo = 'Tatuagem'
        AND m.estado = 'Concluída'
    """, (alvo,))
    marcacoes = cur.fetchall()
    cur.close(); conn.close()

    for m in marcacoes:
        print(f"  📸 Follow-up: {m['nome']}")
        html = email_foto_followup(m['nome'], m['descricao'])
        enviar_email(m['email'], f"📸 Já passaram 2 semanas — como está a tua tatuagem?", html)

    if not marcacoes:
        print("  (Nenhum follow-up para hoje)")


# ─────────────────────────────────────────────
#  RUNNER PRINCIPAL
# ─────────────────────────────────────────────
def correr_todos():
    print(f"\n{'='*50}")
    print(f"  InkManager — Automação de Emails")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*50}")
    verificar_aniversarios()
    verificar_pre_tattoo()
    verificar_pos_tattoo()
    verificar_followup()
    print(f"\n{'='*50}")
    print("  Concluído!")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    correr_todos()
