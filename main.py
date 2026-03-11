import mysql.connector
import os
import shutil
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES
# ─────────────────────────────────────────────
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "QwertyuioP@1706"
DB_DATABASE = "inkmanager"
FILES_DIR   = "inkmanager_ficheiros"


# ─────────────────────────────────────────────
#  INICIALIZAÇÃO
# ─────────────────────────────────────────────
def inicializar():
    os.makedirs(FILES_DIR, exist_ok=True)

    conn_temp = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    cur = conn_temp.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_DATABASE}")
    cur.close(); conn_temp.close()

    conn = conectar(); cur = conn.cursor()

    # Clientes
    cur.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id               INT AUTO_INCREMENT PRIMARY KEY,
        nome             VARCHAR(255) NOT NULL,
        data_nascimento  DATE,
        telemovel        VARCHAR(20),
        instagram        VARCHAR(255),
        email            VARCHAR(255),
        observacoes      TEXT,
        data_registo     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Marcações (unifica sessões + agendamentos)
    cur.execute('''CREATE TABLE IF NOT EXISTS marcacoes (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        id_cliente   INT NOT NULL,
        data_hora    DATETIME NOT NULL,
        tipo         VARCHAR(50) DEFAULT 'Tatuagem',
        descricao    TEXT,
        valor        DECIMAL(10,2),
        materiais    TEXT,
        duracao      VARCHAR(5),
        estado       VARCHAR(50) DEFAULT 'Pendente',
        notas        TEXT,
        data_registo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
    )''')

    # Ficheiros
    cur.execute('''CREATE TABLE IF NOT EXISTS ficheiros (
        id            INT AUTO_INCREMENT PRIMARY KEY,
        id_cliente    INT NOT NULL,
        nome_ficheiro VARCHAR(255) NOT NULL,
        tipo          VARCHAR(10),
        caminho       VARCHAR(500) NOT NULL,
        descricao     TEXT,
        data_upload   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
    )''')

    conn.commit(); cur.close(); conn.close()


def conectar():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)


# ─────────────────────────────────────────────
#  UTILITÁRIOS
# ─────────────────────────────────────────────
def separador(titulo=""):
    print("\n" + "═"*50)
    if titulo:
        print(f"  {titulo}")
        print("─"*50)

def pausa():
    input("\n  ↵  Prima Enter para continuar...")

def confirmar(msg):
    return input(f"  ⚠️  {msg} (s/n): ").strip().lower() == 's'

def pedir_data_hora(msg):
    while True:
        v = input(f"  {msg} (AAAA-MM-DD HH:MM): ").strip()
        if not v: print("  ⚠️  Campo obrigatório."); continue
        try: datetime.strptime(v, "%Y-%m-%d %H:%M"); return v
        except ValueError: print("  ⚠️  Formato inválido. Usa AAAA-MM-DD HH:MM (ex: 2026-04-01 14:30).")

def pedir_data(msg):
    while True:
        v = input(f"  {msg} (AAAA-MM-DD, Enter para ignorar): ").strip()
        if not v: return None
        try: datetime.strptime(v, "%Y-%m-%d"); return v
        except ValueError: print("  ⚠️  Formato inválido. Usa AAAA-MM-DD (ex: 2026-03-13).")

def pedir_valor(msg):
    while True:
        v = input(f"  {msg} (€, Enter para ignorar): ").strip()
        if not v: return None
        try: return float(v)
        except ValueError: print("  ⚠️  Introduz apenas um número (ex: 70 ou 70.50).")

def pedir_tipo():
    tipos = {'1': 'Tatuagem', '2': 'Consulta', '3': 'Acompanhamento pós-tattoo', '4': 'Outro'}
    print("  Tipo de marcação:")
    for k, v in tipos.items(): print(f"    {k}. {v}")
    op = input("  Opção (Enter = Tatuagem): ").strip()
    return tipos.get(op, 'Tatuagem')

def escolher_cliente(acao="selecionar"):
    listar_clientes()
    while True:
        try:
            raw = input(f"\n  ID do cliente a {acao} (0 para cancelar): ").strip()
            if raw == '0': return None
            val = int(raw)
            if val > 0: return val
            print("  ⚠️  Introduz um número válido.")
        except ValueError: print("  ⚠️  Introduz apenas o número do ID.")


# ─────────────────────────────────────────────
#  CLIENTES
# ─────────────────────────────────────────────
def adicionar_cliente():
    separador("NOVO CLIENTE")
    print("  (Prima Enter para deixar um campo vazio)\n")
    while True:
        nome = input("  Nome completo: ").strip()
        if nome: break
        print("  ⚠️  O nome é obrigatório.")
    data_n = pedir_data("Data de Nascimento")
    tel    = input("  Telemóvel: ").strip() or None
    insta  = input("  Instagram (@): ").strip() or None
    email  = input("  Email: ").strip() or None
    obs    = input("  Observações / alergias: ").strip() or None

    while True:
        print(f"\n  ── RESUMO ──────────────────────────────────")
        print(f"  Nome:        {nome}")
        print(f"  Nascimento:  {data_n or '—'}")
        print(f"  Telemóvel:   {tel or '—'}")
        print(f"  Instagram:   {insta or '—'}")
        print(f"  Email:       {email or '—'}")
        print(f"  Observações: {obs or '—'}")
        print(f"  ────────────────────────────────────────────")
        print("  1. Guardar  |  2. Corrigir campo  |  0. Cancelar")
        op = input("  Opção: ").strip()
        if op == '0': print("  Cancelado."); return
        elif op == '2':
            print("  1.Nome  2.Data Nasc.  3.Telemóvel  4.Instagram  5.Email  6.Observações")
            c = input("  Campo a corrigir: ").strip()
            if c == '1':
                while True:
                    nome = input("  Novo nome: ").strip()
                    if nome: break
                    print("  ⚠️  O nome é obrigatório.")
            elif c == '2': data_n = pedir_data("Nova data de nascimento")
            elif c == '3': tel    = input("  Novo telemóvel: ").strip() or None
            elif c == '4': insta  = input("  Novo Instagram: ").strip() or None
            elif c == '5': email  = input("  Novo email: ").strip() or None
            elif c == '6': obs    = input("  Novas observações: ").strip() or None
        elif op == '1':
            try:
                conn = conectar(); cur = conn.cursor()
                cur.execute('''INSERT INTO clientes (nome,data_nascimento,telemovel,instagram,email,observacoes)
                    VALUES (%s,%s,%s,%s,%s,%s)''', (nome,data_n,tel,insta,email,obs))
                conn.commit(); print(f"\n  ✅ Cliente '{nome}' adicionado!")
                cur.close(); conn.close(); return
            except Exception as e: print(f"  ❌ Erro: {e}")

def listar_clientes():
    separador("LISTA DE CLIENTES")
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT id,nome,telemovel,instagram FROM clientes ORDER BY nome")
        rows = cur.fetchall(); cur.close(); conn.close()
        if not rows: print("  (Ainda não tens clientes registados)"); return
        print(f"  {'ID':<5} {'Nome':<28} {'Telemóvel':<15} {'Instagram'}")
        print("  " + "─"*62)
        for r in rows:
            print(f"  {r[0]:<5} {(r[1] or ''):<28} {(r[2] or ''):<15} {r[3] or ''}")
    except Exception as e: print(f"  ❌ Erro: {e}")

def mostrar_ficha(id_c, conn=None):
    """Mostra os dados do cliente, marcações e ficheiros."""
    fechar = conn is None
    if fechar: conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes WHERE id=%s", (id_c,))
    c = cur.fetchone()
    if not c:
        print("  ❌ Cliente não encontrado.")
        cur.close()
        if fechar: conn.close()
        return False
    print(f"\n  {'ID:':<22}{c[0]}")
    print(f"  {'Nome:':<22}{c[1]}")
    print(f"  {'Data Nasc.:':<22}{c[2] or '—'}")
    print(f"  {'Telemóvel:':<22}{c[3] or '—'}")
    print(f"  {'Instagram:':<22}{c[4] or '—'}")
    print(f"  {'Email:':<22}{c[5] or '—'}")
    print(f"  {'Observações:':<22}{c[6] or '—'}")

    cur.execute('''SELECT id,data_hora,tipo,descricao,valor,duracao,estado
        FROM marcacoes WHERE id_cliente=%s ORDER BY data_hora DESC''',(id_c,))
    rows = cur.fetchall()
    print(f"\n  📅 MARCAÇÕES ({len(rows)})")
    if rows:
        for m in rows:
            icone = "🟡" if m[6]=="Pendente" else ("✅" if m[6]=="Concluída" else "❌")
            valor = f"{m[4]}€" if m[4] else "—"
            dur   = f"{m[5]}h"  if m[5] else "—"
            print(f"     {icone} [{m[0]}] {str(m[1])[:16]}  {m[2]}  |  {(m[3] or '—')[:30]}  |  {valor}  |  {dur}")
    else: print("     (nenhuma marcação)")

    cur.execute('''SELECT id,nome_ficheiro,tipo,descricao FROM ficheiros
        WHERE id_cliente=%s ORDER BY data_upload DESC''',(id_c,))
    rows = cur.fetchall()
    print(f"\n  📎 FICHEIROS ({len(rows)})")
    if rows:
        for f in rows: print(f"     [{f[0]}] {f[1]}  ({f[2]})  |  {f[3] or '—'}")
    else: print("     (nenhum ficheiro)")
    cur.close()
    if fechar: conn.close()
    return True


def ver_ficha_cliente():
    separador("FICHA DE CLIENTE")
    id_c = escolher_cliente("ver")
    if not id_c: return

    while True:
        separador(f"FICHA — CLIENTE #{id_c}")
        if not mostrar_ficha(id_c): return
        print("\n  ─────────────────────────────────────────────")
        print("  1. ➕ Adicionar ficheiro")
        print("  2. 🗑️  Apagar ficheiro")
        print("  0. ← Voltar")
        op = input("\n  Opção: ").strip()
        if op == '0': break
        elif op == '1': adicionar_ficheiro(id_c)
        elif op == '2': apagar_ficheiro(id_c)
        else: print("  ⚠️  Opção inválida.")
        pausa()

def editar_cliente():
    separador("EDITAR CLIENTE")
    id_c = escolher_cliente("editar")
    if not id_c: return
    campos = {'1':('nome','Nome'),'2':('data_nascimento','Data Nasc. (AAAA-MM-DD)'),
              '3':('telemovel','Telemóvel'),'4':('instagram','Instagram'),
              '5':('email','Email'),'6':('observacoes','Observações')}
    print()
    for k,(_,l) in campos.items(): print(f"  {k}. {l}")
    op = input("\n  Campo a alterar: ").strip()
    if op not in campos: print("  ❌ Opção inválida."); return
    campo, label = campos[op]
    novo = input(f"  Novo valor para '{label}': ").strip()
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute(f"UPDATE clientes SET {campo}=%s WHERE id=%s",(novo,id_c))
        conn.commit(); print(f"  ✅ '{label}' atualizado!")
        cur.close(); conn.close()
    except Exception as e: print(f"  ❌ Erro: {e}")

def apagar_cliente():
    separador("APAGAR CLIENTE")
    id_c = escolher_cliente("apagar")
    if not id_c: return
    if not confirmar(f"Apagar cliente ID {id_c} e TODO o histórico?"): print("  Cancelado."); return
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT caminho FROM ficheiros WHERE id_cliente=%s",(id_c,))
        for row in cur.fetchall():
            if os.path.exists(row[0]): os.remove(row[0])
        cur.execute("DELETE FROM clientes WHERE id=%s",(id_c,))
        if cur.rowcount > 0: conn.commit(); print("  ✅ Cliente apagado!")
        else: print("  ⚠️  ID não encontrado.")
        cur.close(); conn.close()
    except Exception as e: print(f"  ❌ Erro: {e}")


# ─────────────────────────────────────────────
#  MARCAÇÕES
# ─────────────────────────────────────────────
def adicionar_marcacao():
    separador("NOVA MARCAÇÃO")
    print("  (Prima Enter para deixar um campo vazio)\n")
    id_c      = escolher_cliente("associar a marcação")
    if not id_c: return
    data_hora = pedir_data_hora("Data e Hora")
    tipo      = pedir_tipo()
    descricao = input("  Descrição: ").strip() or None
    valor     = pedir_valor("Valor")
    materiais = input("  Materiais usados: ").strip() or None
    duracao   = input("  Duração (ex: 1.30=1h30min, 0.30=30min, Enter para ignorar): ").strip() or None
    notas     = input("  Notas: ").strip() or None

    while True:
        print(f"\n  ── RESUMO ──────────────────────────────────")
        print(f"  Data/Hora:  {data_hora}")
        print(f"  Tipo:       {tipo}")
        print(f"  Descrição:  {descricao or '—'}")
        print(f"  Valor:      {str(valor)+'€' if valor else '—'}")
        print(f"  Materiais:  {materiais or '—'}")
        print(f"  Duração:    {str(duracao)+'h' if duracao else '—'}")
        print(f"  Notas:      {notas or '—'}")
        print(f"  ────────────────────────────────────────────")
        print("  1. Guardar  |  2. Corrigir campo  |  0. Cancelar")
        op = input("  Opção: ").strip()
        if op == '0': print("  Cancelado."); return
        elif op == '2':
            print("  1.Data/Hora  2.Tipo  3.Descrição  4.Valor  5.Materiais  6.Duração  7.Notas")
            c = input("  Campo a corrigir: ").strip()
            if c == '1': data_hora = pedir_data_hora("Nova data e hora")
            elif c == '2': tipo      = pedir_tipo()
            elif c == '3': descricao = input("  Nova descrição: ").strip() or None
            elif c == '4': valor     = pedir_valor("Novo valor")
            elif c == '5': materiais = input("  Novos materiais: ").strip() or None
            elif c == '6': duracao   = input("  Nova duração (ex: 1.30): ").strip() or None
            elif c == '7': notas     = input("  Novas notas: ").strip() or None
        elif op == '1':
            try:
                conn = conectar(); cur = conn.cursor()
                cur.execute('''INSERT INTO marcacoes
                    (id_cliente,data_hora,tipo,descricao,valor,materiais,duracao,estado,notas)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,'Pendente',%s)''',
                    (id_c,data_hora,tipo,descricao,valor,materiais,duracao,notas))
                conn.commit(); print("  ✅ Marcação adicionada!")
                cur.close(); conn.close(); return
            except Exception as e: print(f"  ❌ Erro ao guardar: {e}")

def listar_marcacoes(filtro_estado=None):
    separador("MARCAÇÕES")
    try:
        conn = conectar(); cur = conn.cursor()
        if filtro_estado:
            cur.execute('''SELECT m.id,c.nome,m.data_hora,m.tipo,m.descricao,m.valor,m.duracao,m.estado
                FROM marcacoes m JOIN clientes c ON m.id_cliente=c.id
                WHERE m.estado=%s ORDER BY m.data_hora ASC''',(filtro_estado,))
        else:
            cur.execute('''SELECT m.id,c.nome,m.data_hora,m.tipo,m.descricao,m.valor,m.duracao,m.estado
                FROM marcacoes m JOIN clientes c ON m.id_cliente=c.id
                ORDER BY m.data_hora ASC''')
        rows = cur.fetchall(); cur.close(); conn.close()
        if not rows: print(f"  (Nenhuma marcação{' com estado '+filtro_estado if filtro_estado else ''})"); return
        print(f"  {'ID':<5} {'Cliente':<18} {'Data/Hora':<17} {'Tipo':<20} {'Valor':>7} {'Dur.':>5}  {'Estado'}")
        print("  " + "─"*90)
        for r in rows:
            icone = "🟡" if r[7]=="Pendente" else ("✅" if r[7]=="Concluída" else ("❌" if r[7]=="Cancelada" else "🔵"))
            valor = f"{r[5]:.2f}€" if r[5] else "—"
            dur   = f"{r[6]}h"     if r[6] else "—"
            print(f"  {r[0]:<5} {(r[1] or ''):<18} {str(r[2])[:16]:<17} {(r[3] or ''):<20} {valor:>7} {dur:>5}  {icone} {r[7]}")
    except Exception as e: print(f"  ❌ Erro: {e}")

def ver_agenda():
    separador("📅  AGENDA")
    print("  Filtrar por estado:")
    print("  1. Todas as marcações")
    print("  2. Só Pendentes")
    print("  3. Só Concluídas")
    print("  4. Só Canceladas")
    print("  5. Só Adiadas")
    op = input("\n  Opção: ").strip()
    filtros = {'1': None, '2': 'Pendente', '3': 'Concluída', '4': 'Cancelada', '5': 'Adiada'}
    if op not in filtros: print("  ⚠️  Opção inválida."); return
    listar_marcacoes(filtros[op])

def alterar_estado_marcacao():
    separador("ALTERAR ESTADO")
    listar_marcacoes()
    while True:
        try: id_m = int(input("\n  ID da marcação (0 para cancelar): ").strip()); break
        except ValueError: print("  ⚠️  Introduz apenas o número do ID.")
    if id_m == 0: return
    estados = {'1':'Pendente','2':'Concluída','3':'Cancelada','4':'Adiada'}
    print("\n  1. Pendente\n  2. Concluída\n  3. Cancelada\n  4. Adiada")
    op = input("  Novo estado: ").strip()
    if op not in estados: print("  ❌ Opção inválida."); return
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute("UPDATE marcacoes SET estado=%s WHERE id=%s",(estados[op],id_m))
        conn.commit(); print(f"  ✅ Estado → '{estados[op]}'!")
        cur.close(); conn.close()
    except Exception as e: print(f"  ❌ Erro: {e}")

def editar_marcacao():
    separador("EDITAR MARCAÇÃO")
    listar_marcacoes()
    while True:
        try: id_m = int(input("\n  ID da marcação a editar (0 para cancelar): ").strip()); break
        except ValueError: print("  ⚠️  Introduz apenas o número do ID.")
    if id_m == 0: return
    campos = {'1':('data_hora','Data/Hora (AAAA-MM-DD HH:MM)'),'2':('tipo','Tipo'),
              '3':('descricao','Descrição'),'4':('valor','Valor (€)'),
              '5':('materiais','Materiais'),'6':('duracao','Duração (ex: 1.30)'),'7':('notas','Notas')}
    for k,(_,l) in campos.items(): print(f"  {k}. {l}")
    op = input("\n  Campo a alterar: ").strip()
    if op not in campos: print("  ❌ Opção inválida."); return
    campo, label = campos[op]
    novo = input(f"  Novo valor para '{label}': ").strip()
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute(f"UPDATE marcacoes SET {campo}=%s WHERE id=%s",(novo,id_m))
        conn.commit(); print(f"  ✅ Marcação atualizada!")
        cur.close(); conn.close()
    except Exception as e: print(f"  ❌ Erro: {e}")

def apagar_marcacao():
    separador("APAGAR MARCAÇÃO")
    listar_marcacoes()
    while True:
        try: id_m = int(input("\n  ID da marcação a apagar (0 para cancelar): ").strip()); break
        except ValueError: print("  ⚠️  Introduz apenas o número do ID.")
    if id_m == 0: return
    if not confirmar(f"Apagar marcação ID {id_m}?"): print("  Cancelado."); return
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute("DELETE FROM marcacoes WHERE id=%s",(id_m,))
        if cur.rowcount > 0: conn.commit(); print("  ✅ Marcação apagada!")
        else: print("  ⚠️  ID não encontrado.")
        cur.close(); conn.close()
    except Exception as e: print(f"  ❌ Erro: {e}")


# ─────────────────────────────────────────────
#  FICHEIROS
# ─────────────────────────────────────────────
TIPOS_PERMITIDOS = {'.pdf','.png','.jpg','.jpeg','.txt'}

def adicionar_ficheiro(id_c=None):
    separador("ADICIONAR FICHEIRO")
    if id_c is None:
        id_c = escolher_cliente("associar ficheiro")
        if not id_c: return
    while True:
        caminho = input("  Caminho completo do ficheiro\n  (ex: C:\\Users\\nusa\\Desktop\\foto.png): ").strip()
        if os.path.isfile(caminho): break
        print("  ⚠️  Ficheiro não encontrado. Verifica o caminho.")
        if not confirmar("Tentar outro caminho?"): return
    ext = os.path.splitext(caminho)[1].lower()
    if ext not in TIPOS_PERMITIDOS:
        print(f"  ❌ Tipo '{ext}' não suportado. Permitidos: {', '.join(TIPOS_PERMITIDOS)}"); return
    descricao = input("  Descrição (Enter para ignorar): ").strip() or None
    nome_orig = os.path.basename(caminho)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(FILES_DIR, f"cli{id_c}_{ts}_{nome_orig}")
    try: shutil.copy2(caminho, destino)
    except Exception as e: print(f"  ❌ Erro ao copiar: {e}"); return
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute('''INSERT INTO ficheiros (id_cliente,nome_ficheiro,tipo,caminho,descricao)
            VALUES (%s,%s,%s,%s,%s)''',(id_c,nome_orig,ext.lstrip('.'),destino,descricao))
        conn.commit(); print(f"  ✅ Ficheiro '{nome_orig}' guardado!\n  📁 Em: {destino}")
        cur.close(); conn.close()
    except Exception as e: print(f"  ❌ Erro: {e}")

def listar_ficheiros():
    separador("FICHEIROS — TODOS OS CLIENTES")
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute('''SELECT f.id,c.nome,f.nome_ficheiro,f.tipo,f.descricao
            FROM ficheiros f JOIN clientes c ON f.id_cliente=c.id ORDER BY f.data_upload DESC''')
        rows = cur.fetchall(); cur.close(); conn.close()
        if not rows: print("  (Nenhum ficheiro registado)"); return
        print(f"  {'ID':<5} {'Cliente':<22} {'Ficheiro':<30} {'Tipo':<6} {'Descrição'}")
        print("  " + "─"*78)
        for r in rows:
            print(f"  {r[0]:<5} {(r[1] or ''):<22} {(r[2] or ''):<30} {(r[3] or ''):<6} {r[4] or '—'}")
    except Exception as e: print(f"  ❌ Erro: {e}")

def apagar_ficheiro(id_c=None):
    separador("APAGAR FICHEIRO")
    # Mostra só os ficheiros do cliente se vier da ficha
    if id_c:
        try:
            conn = conectar(); cur = conn.cursor()
            cur.execute('''SELECT f.id,f.nome_ficheiro,f.tipo,f.descricao
                FROM ficheiros f WHERE f.id_cliente=%s ORDER BY f.data_upload DESC''',(id_c,))
            rows = cur.fetchall(); cur.close(); conn.close()
            if not rows: print("  (Este cliente não tem ficheiros)"); return
            print(f"  {'ID':<5} {'Ficheiro':<30} {'Tipo':<6} {'Descrição'}")
            print("  " + "─"*60)
            for r in rows: print(f"  {r[0]:<5} {(r[1] or ''):<30} {(r[2] or ''):<6} {r[3] or '—'}")
        except Exception as e: print(f"  ❌ Erro: {e}"); return
    else:
        listar_ficheiros()
    while True:
        try: id_f = int(input("\n  ID do ficheiro a apagar (0 para cancelar): ").strip()); break
        except ValueError: print("  ⚠️  Introduz apenas o número do ID.")
    if id_f == 0: return
    if not confirmar(f"Apagar ficheiro ID {id_f} permanentemente?"): print("  Cancelado."); return
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT caminho,nome_ficheiro FROM ficheiros WHERE id=%s",(id_f,))
        row = cur.fetchone()
        if not row: print("  ⚠️  ID não encontrado."); return
        caminho, nome = row
        if os.path.exists(caminho): os.remove(caminho)
        cur.execute("DELETE FROM ficheiros WHERE id=%s",(id_f,))
        conn.commit(); print(f"  ✅ Ficheiro '{nome}' apagado!")
        cur.close(); conn.close()
    except Exception as e: print(f"  ❌ Erro: {e}")


# ─────────────────────────────────────────────
#  MENUS
# ─────────────────────────────────────────────
def menu_clientes():
    while True:
        separador("👥  CLIENTES")
        print("  1. Adicionar cliente")
        print("  2. Listar clientes")
        print("  3. Ver ficha completa")
        print("  4. Editar cliente")
        print("  5. Apagar cliente")
        print("  0. ← Voltar")
        op = input("\n  Opção: ").strip()
        if op=='1': adicionar_cliente()
        elif op=='2': listar_clientes()
        elif op=='3': ver_ficha_cliente()
        elif op=='4': editar_cliente()
        elif op=='5': apagar_cliente()
        elif op=='0': break
        else: print("  ⚠️  Opção inválida.")
        if op != '0': pausa()

def menu_marcacoes():
    while True:
        separador("📋  MARCAÇÕES")
        print("  1. Nova marcação")
        print("  2. Listar todas as marcações")
        print("  3. Editar marcação")
        print("  4. Alterar estado")
        print("  5. Apagar marcação")
        print("  0. ← Voltar")
        op = input("\n  Opção: ").strip()
        if op=='1': adicionar_marcacao()
        elif op=='2': listar_marcacoes()
        elif op=='3': editar_marcacao()
        elif op=='4': alterar_estado_marcacao()
        elif op=='5': apagar_marcacao()
        elif op=='0': break
        else: print("  ⚠️  Opção inválida.")
        if op != '0': pausa()

def menu_ficheiros():
    while True:
        separador("📎  FICHEIROS")
        print("  1. Adicionar ficheiro  (PDF/PNG/JPG/TXT)")
        print("  2. Listar ficheiros")
        print("  3. Apagar ficheiro")
        print("  0. ← Voltar")
        op = input("\n  Opção: ").strip()
        if op=='1': adicionar_ficheiro()
        elif op=='2': listar_ficheiros()
        elif op=='3': apagar_ficheiro()
        elif op=='0': break
        else: print("  ⚠️  Opção inválida.")
        if op != '0': pausa()

def menu_principal():
    inicializar()
    while True:
        print("\n  ╔══════════════════════════════════════════════╗")
        print("  ║        💉  INKMANAGER  v3.0                  ║")
        print("  ║        CRM para Tatuadores                   ║")
        print("  ╠══════════════════════════════════════════════╣")
        print("  ║   1.  👥  Clientes                           ║")
        print("  ║   2.  📋  Marcações                          ║")
        print("  ║   3.  📅  Agenda                             ║")
        print("  ║   0.  🚪  Sair                               ║")
        print("  ╚══════════════════════════════════════════════╝")
        op = input("\n  Opção: ").strip()
        if op=='1': menu_clientes()
        elif op=='2': menu_marcacoes()
        elif op=='3': ver_agenda(); pausa()
        elif op=='0': print("\n  Até logo! 👋\n"); break
        else: print("  ⚠️  Opção inválida.")

if __name__ == "__main__":
    menu_principal()