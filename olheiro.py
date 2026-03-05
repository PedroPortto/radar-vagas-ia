import requests
from bs4 import BeautifulSoup
import urllib3
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bot_telegram import enviar_mensagem_telegram

# Desativa avisos de segurança chatos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# O perfil que o modelo de ML vai buscar
PERFIL_IDEAL = (
    "machine learning mlops python pytorch tensorflow keras deep learning "
    "redes neurais neural networks artificial intelligence ia generative llm "
    "vision nlp deploy engenheiro cientista data scientist ai engineer"
)

def filtro_ml_inteligente(texto_vaga):
    vectorizer = CountVectorizer()
    vetores = vectorizer.fit_transform([PERFIL_IDEAL, texto_vaga.lower()])
    similaridade = cosine_similarity(vetores[0:1], vetores[1:2])[0][0]
    return similaridade > 0.01 

def buscar_vagas_filtradas():
    print("Iniciando a ronda por vagas de IA postadas nos últimos 90 minutos...")
    
    url = "https://br.linkedin.com/jobs/search?keywords=Machine%20Learning%20Python%20Remoto&location=Brasil&geoId=106057199&f_TPR=r5400"
    
    cabecalho = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resposta = requests.get(url, headers=cabecalho, verify=False, timeout=15)
        site_organizado = BeautifulSoup(resposta.text, 'html.parser')
        
        lista_de_vagas = site_organizado.find_all('div', class_='base-search-card__info')
        
        # Log para sabermos se o LinkedIn bloqueou ou se não tem vaga mesmo
        print(f"DEBUG: Encontrei {len(lista_de_vagas)} vagas no total para analisar.")
        
        if not lista_de_vagas:
            aviso = "Nenhuma vaga recente encontrada nesta rodada."
            print(aviso)
            enviar_mensagem_telegram(aviso)
            return

        for vaga in lista_de_vagas:
            titulo = vaga.find('h3', class_='base-search-card__title').text.strip()
            empresa = vaga.find('h4', class_='base-search-card__subtitle').text.strip()
            local = vaga.find('span', class_='job-search-card__location').text.strip()
            
            link_tag = vaga.find_previous('a', class_='base-card__full-link')
            link = link_tag['href'] if link_tag else "Link indisponivel"

            # Filtro de Localizacao (Rio de Janeiro ou Remoto)
            eh_remoto = any(word in local.lower() for word in ["remoto", "remote", "brasil", "anywhere"])
            eh_rj = "rio de janeiro" in local.lower() or "rj" in local.lower()
            
            if eh_remoto or eh_rj:
                if filtro_ml_inteligente(titulo):
                    # Lista de palavras que tornam a vaga "especial" para voce
                    palavras_premium = ["generative", "llm", "deep learning", "neural", "especialista"]
                    eh_vaga_premium = any(p in titulo.lower() for p in palavras_premium)

                    if eh_vaga_premium:
                        cabecalho_vaga = "ESTA EH A BOA! Vaga de peso encontrada para o futuro Engenheiro de IA"
                    else:
                        cabecalho_vaga = "Nova Vaga Encontrada"

                    mensagem = (
                        f"{cabecalho_vaga}\n\n"
                        f"Cargo: {titulo}\n"
                        f"Empresa: {empresa}\n"
                        f"Local: {local}\n"
                        f"Link: {link}"
                    )
                    
                    enviar_mensagem_telegram(mensagem)
                    print(f"Alerta enviado: {titulo}")
                else:
                    print(f"DEBUG: Titulo ignorado pela IA: {titulo}")
                    enviar_mensagem_telegram(aviso)
            else:
                print(f"DEBUG: Local ignorado: {local}")
                enviar_mensagem_telegram(aviso)

    except Exception as e:
        print(f"Ocorreu um erro na busca: {e}")

if __name__ == "__main__":
    buscar_vagas_filtradas()
