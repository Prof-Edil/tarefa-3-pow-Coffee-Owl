import hashlib
import struct
import os
import multiprocessing
import time

OUTPUT_FILE = 'solutions/exercise03.txt'
ROOT_FILE = 'solutions/exercise02.txt'

# Target: 00000000ffff0000000000000000000000000000000000000000000000000000
TARGET_HEX = "00000000ffff0000000000000000000000000000000000000000000000000000"

def mine_worker(worker_id, start_nonce, step, header_prefix, found_event, result_queue):
    nonce = start_nonce

    # O loop externo verifica se o bloco foi achado por outro processo
    while not found_event.is_set():
        
        # O loop interno é o nosso "lote". Ele minera 500.000 hashes seguidos
        # SEM se comunicar com o sistema operacional. Isso elimina o gargalo!
        for _ in range(500000):
            nonce_bytes = struct.pack('>Q', nonce)
            header = header_prefix + nonce_bytes
            
            block_hash = hashlib.sha256(header).hexdigest()
            
            if block_hash <= TARGET_HEX:
                found_event.set()
                result_queue.put(header.hex())
                return
                
            nonce += step
            
        # Depois de rodar 500 mil tentativas, ele dá um respiro, checa o evento e imprime
        print(f"Trabalhador {worker_id} processou até a faixa do nonce: {nonce}...")

def solve_pow():
    with open(ROOT_FILE, 'r') as f:
        merkle_root_hex = f.readline().strip()

    # Montando o prefixo do cabeçalho
    version = struct.pack('>I', 2) # Version > 1
    prev_block = bytes.fromhex("00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee")
    merkle_root = bytes.fromhex(merkle_root_hex)
    timestamp = struct.pack('>I', 1231000000) # Jan 03 2009 16:26:40 UTC
    
    header_prefix = version + prev_block + merkle_root + timestamp

    print("Iniciando mineração acelerada. Isso deve levar alguns minutos...")
    start_time = time.time()

    num_cores = multiprocessing.cpu_count()
    
    # Usando primitivas nativas de Multiprocessing (muito mais rápido que o Manager)
    found_event = multiprocessing.Event()
    result_queue = multiprocessing.Queue()
    
    processes = []
    
    for i in range(num_cores):
        p = multiprocessing.Process(
            target=mine_worker, 
            args=(i, i, num_cores, header_prefix, found_event, result_queue)
        )
        processes.append(p)
        p.start()

    # Espera até que o bloco seja encontrado
    found_event.wait()
    
    valid_header_hex = result_queue.get()
    
    for p in processes:
        p.terminate()
        p.join()

    end_time = time.time()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(valid_header_hex)

    print(f"\nBOOM! Bloco minerado com sucesso em {end_time - start_time:.2f} segundos!")
    print(f"Header: {valid_header_hex}")

if __name__ == '__main__':
    solve_pow()