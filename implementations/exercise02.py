import hashlib
import os

INPUT_FILE = 'data/ex02_txid_list.txt'
OUTPUT_FILE = 'solutions/exercise02.txt'
TARGET_TX = '49ff8cccf1ca12179e9ae7a4760f550b5a18401b27e1e057604e27c3e10c08fb'

def hash256(byte_data):
    # O exercício pede apenas SHA256 simples (single), não o double SHA256 padrão do Bitcoin
    return hashlib.sha256(byte_data).digest()

def solve_merkle():
    with open(INPUT_FILE, 'r') as f:
        txids = [line.strip() for line in f if line.strip()]

    # Converter hex strings para bytes (big endian)
    # Como as strings hex já estão no formato esperado, bytes.fromhex() lê da esquerda pra direita.
    level = [bytes.fromhex(txid) for txid in txids]
    
    target_index = txids.index(TARGET_TX)
    proof = []

    while len(level) > 1:
        next_level = []
        # Se for ímpar, duplica o último elemento
        if len(level) % 2 != 0:
            level.append(level[-1])
            
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1]
            next_level.append(hash256(left + right))
            
            # Se o nosso alvo está em um desses pares, salvamos o irmão (sibling)
            if i == target_index or i + 1 == target_index:
                sibling_index = i + 1 if i == target_index else i
                proof.append(level[sibling_index].hex())
                
        # Atualiza o índice do alvo para o próximo nível
        target_index = target_index // 2
        level = next_level

    merkle_root = level[0].hex()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(merkle_root + '\n')
        for p in proof:
            f.write(p + '\n')
            
    print(f"Merkle Root: {merkle_root}")
    print(f"Prova gerada com {len(proof)} níveis.")

if __name__ == '__main__':
    solve_merkle()