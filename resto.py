import os
import base64

# Gera uma chave de 32 bytes aleatórios
chave = os.urandom(32)

# Para facilitar o armazenamento e leitura, você pode codificar a chave em base64
chave_base64 = base64.b64encode(chave).decode('utf-8')

# Salva a chave em um arquivo, por exemplo, "aes_key.txt"
with open("aes_key.txt", "w") as arquivo:
    arquivo.write(chave_base64)

print("Chave AES gerada e salva com sucesso!")
