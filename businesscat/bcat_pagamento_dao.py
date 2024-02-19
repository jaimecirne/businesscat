import sqlite3
from datetime import datetime
import time
import logging
import locale
from dateutil.parser import parse

# enable logging
logging.basicConfig(
    # filename=f"log {__name__} pix2txt_bot.log",
    format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# get logger
logger = logging.getLogger(__name__)

conn = sqlite3.connect('dados.db')

cursor = conn.cursor()

# Criar tabela se não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pagamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        nome TEXT,
        valor INTEGER,
        estabelecimento TEXT,
        categoria TEXT,
        quando TEXT       
    )
''')

def adicionar_pagamento(user_id, nome, valor, estabelecimento, categoria, quando):
    # Verificar se já existe um pagamento com os mesmos valores
    cursor.execute('''
        SELECT * FROM pagamento
        WHERE valor = ? AND estabelecimento = ? AND quando = ?
    ''', (valor, estabelecimento, quando.strftime("%Y-%m-%d %H:%M")))

    if cursor.fetchone() is None:    
        # Se não existir, realizar a inserção
        cursor.execute('INSERT INTO pagamento (user_id, nome, valor, estabelecimento, categoria, quando) VALUES (?, ?, ?, ?, ?, ?)', (user_id, nome, valor, estabelecimento, categoria, quando.strftime("%Y-%m-%d %H:%M")))
        conn.commit()
    else:
        raise ValueError("Um pagamento com os mesmos valores já existe no banco de dados.")


def remover_pagamento(user_id, pagamento_id):
    # Verificar se já existe um pagamento com os mesmos valores

    cursor.execute('''
        SELECT * FROM pagamento
        WHERE id = ? AND user_id = ?
    ''', (pagamento_id, user_id))

    if cursor.fetchone() is not None:    
        # Se não existir, realizar a inserção
        cursor.execute('DELETE FROM pagamento WHERE id = ? AND user_id = ?', (int(pagamento_id),user_id ))
        conn.commit()
    else:
        raise ValueError("Um pagamento tem que ser removido pelo usuário que adicionou.")

    conn.commit()

def obter_pagamentos():
    cursor.execute('SELECT * FROM pagamento')
    return cursor.fetchall()