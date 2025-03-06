import cv2
import numpy as np
import datetime
import matplotlib.pyplot as plt
import hashlib
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity

class ImageProcessor:
    def capturar_imagem(self, image_path): 
        """
        Simula a captura de uma imagem (lendo de um arquivo) e anexa metadados (GPS, timestamp).
        """
        imagem = cv2.imread(image_path)
        if imagem is None:
            raise FileNotFoundError("Imagem não encontrada.")
        metadados = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "gps": {"lat": -16.680, "lng": -49.255}  # Coordenadas fictícias
        }
        return imagem, metadados

    def preprocessar_imagem(self, imagem): 
        """
        Detecta, alinha e normaliza o rosto utilizando DeepFace com o backend 'mtcnn'.
        """
        rosto_alinhado = DeepFace.detectFace(imagem, detector_backend='mtcnn')
        if rosto_alinhado is None:
            raise ValueError("Nenhum rosto foi detectado na imagem.")
        return rosto_alinhado

    """def embedding_assinatura(self, rosto_alinhado):
        
        Extrai o embedding facial usando um modelo pré-treinado.
        Em seguida, normaliza/quantiza o vetor e gera uma assinatura consistente (hash SHA-256).
        
        print("Processando embedding")
        resultado = DeepFace.represent(rosto_alinhado, model_name='ArcFace', enforce_detection=False)
        embedding = np.array(resultado)  
        embedding_normalizado = np.round(embedding, decimals=3)
        embedding_str = str(embedding_normalizado.tolist())
        assinatura = hashlib.sha256(embedding_str.encode()).hexdigest()
        return embedding_normalizado, assinatura"""
    
    def embedding_assinatura(self, rosto_alinhado):
        """
        Extrai o embedding facial usando um modelo pré-treinado.
        Em seguida, normaliza/quantiza o vetor e gera uma assinatura usando LSH.
        Essa assinatura é gerada com base em hiperplanos aleatórios, de modo que embeddings semelhantes
        produzirão assinaturas similares.
        """
        print("Processando embedding")
        # Extrai o embedding usando o DeepFace
        resultado = DeepFace.represent(rosto_alinhado, model_name='ArcFace', enforce_detection=False)
        embedding = np.array(resultado)
        # Normaliza/quantiza o embedding
        embedding_normalizado = np.round(embedding, decimals=3)
        
        # Gera a assinatura LSH:
        # Se os hiperplanos LSH ainda não foram criados, criamos com base na dimensão do embedding.
        if not hasattr(self, 'lsh_planes'):
            self.lsh_dim = 64  # Número de hiperplanos (pode ajustar conforme necessário)
            dim = embedding_normalizado.shape[0]
            # Gera hiperplanos com distribuição normal
            self.lsh_planes = np.random.randn(dim, self.lsh_dim)
        
        # Calcula as projeções do embedding sobre os hiperplanos
        projections = np.dot(embedding_normalizado, self.lsh_planes)
        # Para cada projeção, se for >= 0, o bit é '1'; caso contrário, '0'
        bits = ['1' if x >= 0 else '0' for x in projections]
        assinatura = ''.join(bits)
        
        return embedding_normalizado, assinatura



    def comparar_embedding(self, embedding, db, threshold=0.7):
        """
        Compara o embedding capturado com os embeddings armazenados na base de dados (db)
        utilizando similaridade cosseno.
        Retorna o ID do perfil se a similaridade for maior que o threshold.
        """
        for id_perfil, emb_db in db:
            sim = cosine_similarity([embedding], [emb_db])[0][0]
            if sim >= threshold:
                return id_perfil, sim
        return None, None

if __name__ == "__main__":
    try:
        processor = ImageProcessor()
        
        imagem, metadados = processor.capturar_imagem("pastor_bandido.jpg")
        rosto_alinhado1 = processor.preprocessar_imagem(imagem)
        
        imagem2, metadados = processor.capturar_imagem("image.png")
        rosto_alinhado2 = processor.preprocessar_imagem(imagem2)
        
        plt.imshow(rosto_alinhado1)
        plt.title("Rosto Alinhado")
        plt.axis("off")
        plt.show()
        
        plt.imshow(rosto_alinhado2)
        plt.title("Rosto Alinhado")
        plt.axis("off")
        plt.show()
        
        e1 = processor.embedding_assinatura(rosto_alinhado1)
        db = [("perfil1", e1[0])]  # Note que no banco armazenamos apenas o embedding
        e2 = processor.embedding_assinatura(rosto_alinhado2)
        
        r1, r2 = processor.comparar_embedding(e2[0], db)
        print(f"Id do perfil: {r1} e similaridade: {r2}")
    
    except Exception as e:
        print("Erro durante o teste:", e)
