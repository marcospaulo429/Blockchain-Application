# blockchain.py
import os
import json
import base64
from web3 import Web3
import ipfshttpclient
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from imagem import ImageProcessor
import base64

def read_aes_key(caminho="aes_key.txt"):
    with open(caminho, "r") as arquivo:
        chave_base64 = arquivo.read().strip()

    return base64.b64decode(chave_base64)

class BlockchainHandler:
    
    AES_KEY = read_aes_key()
    AES_BLOCK_SIZE = 16
    BLOCKCHAIN_NODE = "http://127.0.0.1:8545"
    CONTRACT_ADDRESS = "0xSeuEnderecoDoContrato"  # Substitua pelo endereço real
    CONTRACT_ABI = [
        {
            "constant": True,
            "inputs": [
                {"name": "assinatura", "type": "bytes32"}
            ],
            "name": "consultarPerfil",
            "outputs": [
                {"name": "ativo", "type": "bool"},
                {"name": "idPessoa", "type": "string"},
                {"name": "ipfsHash", "type": "string"},
                {"name": "timestamp", "type": "uint256"}
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
    ]
    
    def __init__(self):
        self.w3, self.contract = self.conectar_blockchain()
    
    def conectar_blockchain(self):
        w3 = Web3(Web3.HTTPProvider(self.BLOCKCHAIN_NODE))
        if not w3.is_connected():
            raise ConnectionError("Não foi possível conectar ao nó blockchain.")
        contract = w3.eth.contract(address=self.CONTRACT_ADDRESS, abi=self.CONTRACT_ABI)
        return w3, contract


    def consultar_perfil(self, assinatura_hex):#TODO
        """
        Consulta o smart contract para verificar se a assinatura corresponde a um perfil.
        Converte a assinatura para bytes32 conforme exigido.
        """
        assinatura_bytes = bytes.fromhex(assinatura_hex)
        perfil = self.contract.functions.consultarPerfil(assinatura_bytes).call()
        return perfil

    def criptografar_dados(self, dados_str, chave=None): #TODO
        """
        Criptografa os dados (string) usando AES-256 em modo CBC.
        Retorna o IV e o ciphertext.
        """
        if chave is None:
            chave = self.AES_KEY
        iv = os.urandom(self.AES_BLOCK_SIZE)
        cipher = AES.new(chave, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(dados_str.encode(), self.AES_BLOCK_SIZE))
        return iv, ciphertext

    def armazenar_no_ipfs(self, iv, ciphertext): #TODO
        """
        Armazena os dados encriptados (junto com o IV) no IPFS e retorna o CID.
        """
        try:
            client = ipfshttpclient.connect()
            dados_para_armazenar = {
                "iv": base64.b64encode(iv).decode(),
                "ciphertext": base64.b64encode(ciphertext).decode()
            }
            dados_json = json.dumps(dados_para_armazenar)
            cid = client.add_str(dados_json)
            client.close()
            return cid
        except Exception as e:
            raise ConnectionError(f"Erro ao armazenar no IPFS: {e}")
        
    def armazenar_lsh_mapping(self, lsh, cid):#TODO
        """
        Armazena o mapeamento entre a assinatura LSH e o CID dos dados encriptados no IPFS.
        Retorna o CID do mapeamento.
        """
        try:
            client = ipfshttpclient.connect()
            mapping_data = {
                "lsh": lsh,
                "cid": cid
            }
            mapping_json = json.dumps(mapping_data)
            mapping_cid = client.add_str(mapping_json)
            client.close()
            return mapping_cid
        except Exception as e:
            raise ConnectionError(f"Erro ao armazenar mapeamento LSH no IPFS: {e}")

        
if __name__ == "__main__":
    try:
        processor = ImageProcessor()
        imagem, metadados = processor.capturar_imagem("pastor_bandido.jpg")
        rosto_alinhado = processor.preprocessar_imagem(imagem)
        embedding, assinatura = processor.embedding_assinatura(rosto_alinhado)  # 'assinatura' agora é a assinatura LSH

        # Prepara os dados que serão armazenados (embedding, assinatura LSH e metadados)
        dados_para_armazenar = {
            "embedding": embedding.tolist(),  # converter para lista para serialização
            "lsh": assinatura,
            "metadados": metadados
        }
        dados_str = json.dumps(dados_para_armazenar)

        # Criptografa os dados
        blockchain_handler = BlockchainHandler()
        iv, ciphertext = blockchain_handler.criptografar_dados(dados_str)

        # Armazena os dados encriptados no IPFS e obtém o CID
        cid = blockchain_handler.armazenar_no_ipfs(iv, ciphertext)
        print("Os dados foram armazenados no IPFS com o CID:", cid)

        # Armazena o mapeamento LSH-CID em outro arquivo no IPFS
        mapping_cid = blockchain_handler.armazenar_lsh_mapping(assinatura, cid)
        print("O mapeamento LSH foi armazenado no IPFS com o CID:", mapping_cid)

    except Exception as e:
        print("Erro durante o teste:", e)
