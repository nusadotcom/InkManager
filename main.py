import sqlite3

# Função para ligar à base de dados
def conectar():
    return sqlite3.connect('inkmanager.db')

# --- FUNCIONALIDADES ---

def adicionar_cliente():
    print("\n--- NOVO CLIENTE ---")
    nome = input("Nome do cliente: ")
    data_nasc = input("Data de Nascimento (AAAA-MM-DD): ")
    telemovel = input("Telemóvel: ")
    instagram = input("Instagram (opcional): ")
    
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        # Inserir os dados na tabela clientes
        cursor.execute('''
            INSERT INTO clientes (nome, data_nascimento, telemovel, instagram)
            VALUES (?, ?, ?, ?)
        ''', (nome, data_nasc, telemovel, instagram))
        
        conn.commit()
        print(f"✅ Cliente '{nome}' adicionado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao adicionar cliente: {e}")
    finally:
        conn.close()

def listar_clientes():
    print("\n--- LISTA DE CLIENTES ---")
    conn = conectar()
    cursor = conn.cursor()
    
    # Ir buscar todos os clientes à base de dados
    cursor.execute("SELECT id, nome, telemovel, instagram FROM clientes")
    clientes = cursor.fetchall() # Guarda os resultados numa lista
    
    if len(clientes) == 0:
        print("Ainda não tens clientes registados.")
    else:
        # Mostrar os clientes de forma organizada
        for cliente in clientes:
            print(f"ID: {cliente[0]} | Nome: {cliente[1]} | Tel: {cliente[2]} | Insta: {cliente[3]}")
            
    conn.close()

# --- MENU PRINCIPAL ---

def menu():
    while True:
        print("\n" + "="*30)
        print("💉 INKMANAGER - Menu Principal")
        print("="*30)
        print("1. Adicionar novo cliente")
        print("2. Listar todos os clientes")
        print("0. Sair")
        print("="*30)
        
        opcao = input("Escolhe uma opção: ")
        
        if opcao == '1':
            adicionar_cliente()
        elif opcao == '2':
            listar_clientes()
        elif opcao == '0':
            print("A fechar o InkManager... Até logo!")
            break
        else:
            print("⚠️ Opção inválida. Tenta novamente.")

# Arrancar o programa
if __name__ == "__main__":
    menu()
