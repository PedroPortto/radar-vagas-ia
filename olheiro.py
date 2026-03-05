import requests
from bs4 import BeautifulSoup
import urllib3
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Importamos a função que você criou para falar com o Telegram
from bot_telegram import enviar_mensagem_telegram

# Desativa avisos de segurança para o script não travar no seu firewall
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Este é o "DNA" das vagas que você quer. O modelo de ML vai comparar isso com o título da vaga.
# Foquei em Deep Learning, Redes Neurais e IA Generativa, conforme seu interesse.
PERFIL_IDEAL = (
    "machine learning mlops python pytorch tensorflow keras deep learning "
    "redes neurais neural networks artificial intelligence ia generative llm "
    "vision nlp deploy engenheiro cientista data scientist ai engineer"
)

def filtro_ml_inteligente(texto_vaga):
    """
    Usa Processamento de Linguagem Natural (NLP) para medir o quanto o título 
    da vaga combina com o seu objetivo de carreira.
    """
    vectorizer = CountVectorizer()
    # Transforma o perfil e o título em números (vetores)
    vetores = vectorizer.fit_transform([PERFIL_IDEAL, texto_vaga.lower()])
    # Calcula a similaridade de cosseno (o quão "perto" os textos estão um do outro)
    similaridade = cosine_similarity(vetores[0:1], vetores[1:2])[0][0]
    return similaridade > 0.01 

def buscar_vagas_filtradas():
    print("Iniciando a ronda por vagas de IA postadas nos últimos 90 minutos...")
    
    # URL configurada para: 
    # 1. Palavras-chave: Machine Learning Python Remoto
    # 2. Local: Brasil (geoId 106057199)
    # 3. Tempo: f_TPR=r5400 (últimos 5400 segundos = 1.5 horas)
    url = "https://br.linkedin.com/jobs/search?keywords=Machine%20Learning%20Python%20Remoto&location=Brasil&geoId=106057199&f_TPR=r5400"
    
    cabecalho = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Acessa o site ignorando erros de certificado SSL (verify=False)
        resposta = requests.get(url, headers=cabecalho, verify=False, timeout=15)
        site_organizado = BeautifulSoup(resposta.text, 'html.parser')
        
        # Encontra os blocos de informação de cada vaga
        lista_de_vagas = site_organizado.find_all('div', class_='base-search-card__info')
        
        if not lista_de_vagas:
            mensagemTelegram = "Nenhuma vaga recente encontrada nesta rodada."
            enviar_mensagem_telegram(mensagemTelegram)
            return

        for vaga in lista_de_vagas:
            # Extração de dados básicos
            titulo = vaga.find('h3', class_='base-search-card__title').text.strip()
            empresa = vaga.find('h4', class_='base-search-card__subtitle').text.strip()
            local = vaga.find('span', class_='job-search-card__location').text.strip()
            
            # Busca o link da vaga (ele fica em uma tag anterior ao bloco de info)
            link_tag = vaga.find_previous('a', class_='base-card__full-link')
            link = link_tag['href'] if link_tag else "Link indisponível"

            # 1. Filtro de Localização (Seu pedido: RJ ou Remoto)
            # Consideramos "Brasil" como indicação de vaga remota nacional
            eh_remoto = any(word in local.lower() for word in ["remoto", "remote", "brasil", "anywhere"])
            eh_rj = "rio de janeiro" in local.lower() or "rj" in local.lower()
            
            if eh_remoto or eh_rj:
                # 2. Filtro de Machine Learning (O cérebro do scikit-learn)
                if filtro_ml_inteligente(titulo):
                    mensagem = (
                        f"🎯 Nova Vaga Encontrada!\n\n"
                        f"Cargo: {titulo}\n"
                        f"Empresa: {empresa}\n"
                        f"Local: {local}\n"
                        f"Link: {link}"
                    )
                    # Envia para o seu Telegram pessoal
                    enviar_mensagem_telegram(mensagem)
                    print(f"✅ Alerta enviado: {titulo}")
                else:
                    print(f"DEBUG: Título ignorado pelo ML: {titulo}")
            else:
                print(f"DEBUG: Local ignorado: {local}")

    except Exception as e:
        print(f"Ocorreu um erro na busca: {e}")

if __name__ == "__main__":
    buscar_vagas_filtradas()