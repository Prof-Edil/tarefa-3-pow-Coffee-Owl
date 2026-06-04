import csv
import os

MEMPOOL_FILE = 'data/mempool.csv'
OUTPUT_FILE = 'solutions/exercise01.txt'
MAX_WEIGHT = 4000000
MANDATORY_TX = '4c50e3dad7f98bceb6441f96b23748dea84fbdb7cedd603441e6ea4a574d04a6'

def get_all_ancestors(txid, mempool, cache):
    if txid in cache:
        return cache[txid]
    ancestors = set()
    for parent in mempool[txid]['parents']:
        ancestors.add(parent)
        ancestors.update(get_all_ancestors(parent, mempool, cache))
    cache[txid] = ancestors
    return ancestors

def solve_mempool():
    mempool = {}
    
    # 1. Carregar mempool
    with open(MEMPOOL_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0] == 'txid': continue # Pula cabeçalho ou linhas vazias
            txid, fee, weight, parents_str = row[0], int(row[1]), int(row[2]), row[3]
            parents = parents_str.split(';') if parents_str else []
            mempool[txid] = {'fee': fee, 'weight': weight, 'parents': parents}
            
    # 2. Calcular ancestrais para cada tx
    ancestors_cache = {}
    for txid in mempool:
        get_all_ancestors(txid, mempool, ancestors_cache)

    selected_txs = []
    selected_set = set()
    current_weight = 0
    current_fees = 0

    def add_tx(tx_id):
        nonlocal current_weight, current_fees
        if tx_id not in selected_set:
            selected_txs.append(tx_id)
            selected_set.add(tx_id)
            current_weight += mempool[tx_id]['weight']
            current_fees += mempool[tx_id]['fee']

    # 3. Adicionar a transação obrigatória e seus ancestrais (em ordem topológica)
    mandatory_chain = list(ancestors_cache[MANDATORY_TX]) + [MANDATORY_TX]
    # Uma forma simples de garantir ordem topológica: ordenar por quantidade de ancestrais
    mandatory_chain.sort(key=lambda x: len(ancestors_cache[x]))
    for tx in mandatory_chain:
        add_tx(tx)

    # 4. Preencher o resto do bloco de forma gulosa
    while True:
        best_tx = None
        best_score = -1
        
        for txid, data in mempool.items():
            if txid in selected_set:
                continue
            
            # Só podemos adicionar se todos os pais já estiverem no bloco
            if all(p in selected_set for p in data['parents']):
                if current_weight + data['weight'] <= MAX_WEIGHT:
                    score = data['fee'] / data['weight']
                    if score > best_score:
                        best_score = score
                        best_tx = txid
                        
        if best_tx is None:
            break # Não cabe mais nada ou não há transações válidas
        
        add_tx(best_tx)

    # 5. Salvar resultado
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        for tx in selected_txs:
            f.write(f"{tx}\n")

    print(f"Bloco montado! Transações: {len(selected_txs)}, Peso: {current_weight}, Taxas: {current_fees} sats")

if __name__ == '__main__':
    solve_mempool()