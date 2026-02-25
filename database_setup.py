import sqlite3

def criar_base_dados():
    # Conectar à base de dados (cria o ficheiro se não existir)
    conn = sqlite3.connect('inkmanager.db')
    cursor = conn.cursor()

    # 1. Tabela de CLIENTES
    # Guardamos o essencial + Instagram para contacto fácil
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data_nascimento TEXT,     -- Formato YYYY-MM-DD para calcular idade fácil
        telemovel TEXT,
        instagram TEXT,
        email TEXT,
        observacoes TEXT,         -- Para alergias ou notas extra
        data_registo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Tabela de SESSÕES (Histórico de Tatuagens)
    # Ligada ao cliente pelo id_cliente (Foreign Key)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER NOT NULL,
        data_sessao TEXT,
        descricao_tattoo TEXT,    -- Ex: "Rosa no ombro direito"
        valor_cobrado REAL,
        materiais_usados TEXT,    -- Ex: "Tinta Dynamic Black, Agulha 3RL"
        foto_path TEXT,           -- Caminho para a foto no computador (opcional)
        FOREIGN KEY (id_cliente) REFERENCES clientes (id)
    )
    ''')

    print("Base de dados 'inkmanager.db' criada com sucesso!")
    
    conn.commit()
    conn.close()

# Executar a função
if __name__ == "__main__":
    criar_base_dados()
