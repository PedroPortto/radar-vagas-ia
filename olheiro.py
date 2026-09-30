import os
import time
import requests
from bs4 import BeautifulSoup
import urllib3
from google import genai
from bot_telegram import enviar_mensagem_telegram
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def avaliar_vaga_gemini(titulo, empresa, local):
    prompt = f"""
Você é um recrutador sênior especialista em segurança da informação e TI.
Avalie esta vaga para um analista de SOC júnior/pleno de 23 anos, 
focado em segurança defensiva, que busca evoluir na carreira.

Vaga:
- Cargo: {titulo}
- Empresa: {empresa}
- Local: {local}

Dê uma nota de 0 a 10 para o quanto essa vaga é relevante para esse perfil.
Responda APENAS com o número inteiro, sem texto adicional.
"""
    for tentativa in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            nota_texto = response.text.strip()
            nota = int(''.join(filter(str.isdigit, nota_texto)))
            return min(nota, 10)
        except Exception as e:
            if tentativa == 0:
                print(f"Gemini erro, tentando de novo em 3s: {e}")
                time.sleep(3)
            else:
                print(f"Gemini falhou: {e}")
                return 0

def buscar_vagas():
    print("Iniciando busca de vagas no LinkedIn...")

    urls = [
        "https://br.linkedin.com/jobs/search?keywords=Analista+de+Seguranca&location=Brasil&geoId=106057199&f_TPR=r86400",
        "https://br.linkedin.com/jobs/search?keywords=SOC+Analyst&location=Brasil&geoId=106057199&f_TPR=r86400",
        "https://br.linkedin.com/jobs/search?keywords=Cybersecurity+Analista&location=Brasil&geoId=106057199&f_TPR=r86400",
    ]

    cabecalho = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    vagas_enviadas = 0

    for url in urls:
        try:
            resposta = requests.get(url, headers=cabecalho, verify=False, timeout=15)
            soup = BeautifulSoup(resposta.text, 'html.parser')
            lista_vagas = soup.find_all('div', class_='base-search-card__info')

            if not lista_vagas:
                print(f"Nenhuma vaga encontrada em: {url}")
                continue

            for vaga in lista_vagas:
                try:
                    titulo = vaga.find('h3', class_='base-search-card__title').text.strip()
                    empresa = vaga.find('h4', class_='base-search-card__subtitle').text.strip()
                    local = vaga.find('span', class_='job-search-card__location').text.strip()
                    link_tag = vaga.find_previous('a', class_='base-card__full-link')
                    link = link_tag['href'] if link_tag else "Link indisponível"

                    print(f"Analisando: {titulo} | {empresa}")
                    nota = avaliar_vaga_gemini(titulo, empresa, local)
                    print(f"Nota Gemini: {nota}/10")

                    if nota >= 7:
                        mensagem = (
                            f"Nova Vaga - Nota {nota}/10\n\n"
                            f"Cargo: {titulo}\n"
                            f"Empresa: {empresa}\n"
                            f"Local: {local}\n"
                            f"Link: {link}"
                        )
                        enviar_mensagem_telegram(mensagem)
                        vagas_enviadas += 1
                        time.sleep(2)

                except Exception as e:
                    print(f"Erro ao processar vaga: {e}")
                    continue

        except Exception as e:
            print(f"Erro ao acessar URL: {e}")
            continue

    if vagas_enviadas == 0:
        enviar_mensagem_telegram("Nenhuma vaga relevante encontrada nesta rodada.")

    print(f"Busca finalizada. {vagas_enviadas} vagas enviadas.")

if __name__ == "__main__":
    buscar_vagas()
