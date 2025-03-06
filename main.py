# main.py
import datetime
import json
import numpy as np
from imagem import ImageProcessor
from blockchain import BlockchainHandler

# Simulação de uma base de dados off-chain com embeddings de perfis criminosos
criminal_db = {
    "criminal_001": np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]),
    # Adicione outros perfis conforme necessário
}

def alertar_autoridades(info_alerta):
    """
    Simula o disparo de alertas para as autoridades.
    """
    print("ALERTA! Perfil criminoso identificado!")
    print("Detalhes do alerta:", info_alerta)
    # Integre com envio de SMS, e-mail ou outra API de notificação

def registrar_ocorrencia(log_info):
    """
    Registra a ocorrência para auditoria.
    """
    print("Ocorrência registrada:", log_info)
    # Em produção, registre essa informação em um sistema de logs seguro ou em blockchain

def main():
    try:
        img_proc = ImageProcessor()
        blockchain_handler = BlockchainHandler()
        
        imagem, metadados = img_proc.capturar_imagem()
        print("Imagem capturada com metadados:", metadados)
        rosto_alinhado = img_proc.preprocessar_imagem(imagem)
        print("Rosto detectado, alinhado e normalizado.")
        embedding, assinatura = img_proc.extrair_embedding(rosto_alinhado)
        print("Embedding extraído e assinatura gerada:", assinatura)
        
        # Comparação Off-Chain
        id_match, similaridade = img_proc.comparar_embedding(embedding, criminal_db)
        if id_match:
            print(f"Correspondência encontrada: {id_match} com similaridade {similaridade:.2f}")
        else:
            print("Nenhuma correspondência encontrada. Processo encerrado.")
            return
        
        # Armazenamento e Controle via IPFS (Exemplo de armazenamento de dados sensíveis)
        dados_sensiveis = json.dumps({
            "imagem": "dados_da_imagem_em_base64_ou_url",
            "metadados": metadados,
            "info_extra": "Outras informações relevantes"
        })
        iv, ciphertext = blockchain_handler.criptografar_dados(dados_sensiveis)
        cid = blockchain_handler.armazenar_no_ipfs(iv, ciphertext)
        print("Dados sensíveis encriptados e armazenados no IPFS com CID:", cid)
        
        # Consulta ao Blockchain
        perfil = blockchain_handler.consultar_perfil(assinatura)
        ativo, idPessoa, ipfsHash, timestamp = perfil
        if ativo:
            print("Perfil criminoso confirmado no blockchain!")
            print(f"ID: {idPessoa}, IPFS Hash: {ipfsHash}, Timestamp: {timestamp}")
        else:
            print("Perfil não ativo ou não encontrado no blockchain.")
            return
        
        # PASSO 7: Resposta
        info_alerta = {
            "idPessoa": idPessoa,
            "cid": cid,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        alertar_autoridades(info_alerta)
        registrar_ocorrencia(info_alerta)
        
    except Exception as e:
        print("Erro durante o processamento:", e)

if __name__ == "__main__":
    main()
