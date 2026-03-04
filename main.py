import mysql.connector

# --- CONFIGURAÇÕES DO MYSQL ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_DATABASE = "inkmanager"

# --- 1. INICIALIZAÇÃO AUTOMÁTICA ---
def inicializar_bd():
    try:
        # Liga ao MySQL
        conn_temp = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
        cursor_temp = conn_temp.cursor()
        cursor_temp.execute(f"CREATE DATABASE IF NOT EXISTS {DB_DATABASE}")
        cursor_temp.close()
        conn_temp.close()

        # Liga à base de dados correta e cria a tabela clientes
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            data_nascimento DATE,
            telemovel VARCHAR(20),
            instagram VARCHAR(255),
            email VARCHAR(255),
            observacoes TEXT,
            data_registo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Erro ao preparar a Base de Dados: {e}")
        print("Verifica se a password do MySQL na linha 6 está correta!")

# Função para ligar à base de dados MySQL
def conectar():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE
    )

# --- 2. FUNCIONALIDADES CRUD ---

def adicionar_cliente():
    print("\n--- NOVO CLIENTE ---")
    nome = input("Nome do cliente: ")
    data_nasc = input("Data de Nascimento (AAAA-MM-DD): ")
    telemovel = input("Telemóvel: ")
    instagram = input("Instagram (opcional): ")

    try:
        conn = conectar()
        cursor = conn.cursor()
        # No MySQL usamos %s
        cursor.execute('''
        INSERT INTO clientes (nome, data_nascimento, telemovel, instagram)
        VALUES (%s, %s, %s, %s)
        ''', (nome, data_nasc, telemovel, instagram))
        conn.commit()
        print(f"✅ Cliente '{nome}' adicionado com sucesso!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao adicionar: {e}")

def listar_clientes():
    print("\n--- LISTA DE CLIENTES ---")
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, telemovel, instagram FROM clientes")
        clientes = cursor.fetchall()
        
        if len(clientes) == 0:
            print("Ainda não tens clientes registados.")
        else:
            for c in clientes:
                print(f"ID: {c[0]} | Nome: {c[1]} | Tel: {c[2]} | Insta: {c[3]}")
        cursor.close()
        conn.close()
    except Exception as e:
         print(f"❌ Erro ao listar: {e}")

def editar_cliente():
    print("\n--- EDITAR CLIENTE ---")
    listar_clientes() 
    try:
        id_cliente = input("\nDigita o ID do cliente que queres alterar (ou 0 para cancelar): ")
        if id_cliente == '0': return

        print("O que queres alterar?\n1. Nome\n2. Telemóvel\n3. Instagram")
        opcao = input("Opção (1/2/3): ")

        if opcao == '1':
            campo, novo_valor = 'nome', input("Novo Nome: ")
        elif opcao == '2':
            campo, novo_valor = 'telemovel', input("Novo Telemóvel: ")
        elif opcao == '3':
            campo, novo_valor = 'instagram', input("Novo Instagram: ")
        else:
            print("⚠️ Opção inválida!")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE clientes SET {campo} = %s WHERE id = %s", (novo_valor, id_cliente))
        conn.commit()
        print("✅ Cliente atualizado com sucesso!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao atualizar: {e}")

def apagar_cliente():
    print("\n--- APAGAR CLIENTE ---")
    listar_clientes() 
    try:
        id_cliente = input("\nDigita o ID do cliente a APAGAR (ou 0 para cancelar): ")
        if id_cliente == '0': return

        conf = input(f"⚠️ Certeza que queres apagar o ID {id_cliente}? (s/n): ")
        if conf.lower() == 's':
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
            if cursor.rowcount > 0:
                conn.commit()
                print("✅ Cliente apagado com sucesso!")
            else:
                print("⚠️ ID não encontrado.")
            cursor.close()
            conn.close()
        else:
            print("Cancelado.")
    except Exception as e:
        print(f"❌ Erro ao apagar: {e}")

# --- 3. MENU PRINCIPAL ---

def menu():
    # Inicializa a BD mal o menu arranca
    inicializar_bd()
    
    while True:
        print("\n" + "="*40)
        print("💉 INKMANAGER - Menu Principal (MySQL)")
        print("="*40)
        print("1. Adicionar novo cliente")
        print("2. Listar todos os clientes")
        print("3. Editar cliente")
        print("4. Apagar cliente")
        print("0. Sair")
        print("="*40)
        
        op = input("Escolhe uma opção: ")
        
        if op == '1': adicionar_cliente()
        elif op == '2': listar_clientes()
        elif op == '3': editar_cliente()
        elif op == '4': apagar_cliente()
        elif op == '0':
            print("A fechar o InkManager... Até logo!")
            break
        else:
            print("⚠️ Opção inválida.")

if __name__ == "__main__":
    menu()