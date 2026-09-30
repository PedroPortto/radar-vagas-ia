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

def avaliar_vagas_gemini(vagas):
    linhas = []
    for i, v in enumerate(vagas):
        linhas.append(f"{i+1}. {v['titulo']} | {v['empresa']} | {v['local']}")

    lista_texto = "\n".join(linhas)

    prompt = f"""Voce e um recrutador senior especialista em seguranca da informacao.

Avalie as vagas abaixo para o seguinte candidato:
- Nome: Pedro Porto, 23 anos, Rio de Janeiro
- Cargo atual: Analista de Infraestrutura e Seguranca da Informacao (SOC) no setor publico
- Experiencia: 3 anos em TI, sendo 1 ano em SOC/Blue Team

Habilidades principais:
- SIEM: Wazuh, Security Onion, Graylog — uso diario em producao
- Firewall: Palo Alto PA-850 (rulebase, VPN GlobalProtect, politicas por grupo AD)
- Gestao de vulnerabilidades: CVEs, remediacao em RHEL 10 e Windows Server 2022
- Active Directory, DNS, GPO, administracao de dominio
- Automacao: n8n, Python, PowerShell, Bash
- Monitoramento: Zabbix, Grafana, Proxmox
- Dados: PostgreSQL, Power BI, DAX, SQL
- Endpoint: Trend Micro Vision One, GLPI 11.0.5
- Seguranca ofensiva basica: nmap, sqlmap, Burp, OWASP Top 10
- Certificacao: CompTIA Security+ (concluida)
- Estudante de Ciencia da Computacao (UVA, formatura 2026)

O candidato busca:
- Vagas de Analista de Seguranca, SOC Analyst, Blue Team, Infraestrutura de Seguranca
- Preferencialmente remoto ou Rio de Janeiro
- Pode ser junior ou pleno
- Quer crescer para red team/pentest no futuro, entao vagas que combinem as duas areas tambem sao bem-vindas

Criterios de avaliacao:
- Nota 9-10: vaga perfeita — SOC, Blue Team, Seguranca da Informacao, combina com habilidades tecnicas
- Nota 7-8: boa vaga — area de seguranca ou infraestrutura com componente de seguranca
- Nota 4-6: vaga ok — TI geral, suporte senior, infraestrutura sem seguranca
- Nota 1-3: pouco relevante — desenvolvimento, dados puros, area muito diferente
- Nota 0: completamente fora do perfil

Responda APENAS com uma linha por vaga no formato: NUMERO|NOTA
Sem texto adicional, sem explicacao, sem cabecalho.

{lista_texto}"""

    for tentativa in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            resultado = {}
            for linha in response.text.strip().split("\n"):
                linha = linha.strip()
                if "|" in linha:
                    partes = linha.split("|")
                    numero = int(''.join(filter(str.isdigit, partes[0])))
                    nota = int(''.join(filter(str.isdigit, partes[1])))
                    resultado[numero] = min(nota, 10)
            return resultado
        except Exception as e:
            if tentativa == 0:
                print(f"Gemini erro, tentando de novo em 3s: {e}")
                time.sleep(3)
            else:
                print(f"Gemini falhou definitivamente: {e}")
                return {}

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

    todas_vagas = []

    for url in urls:
        try:
            resposta = requests.get(url, headers=cabecalho, verify=False, timeout=15)
            soup = BeautifulSoup(resposta.text, 'html.parser')
            lista = soup.find_all('div', class_='base-search-card__info')

            for vaga in lista:
                try:
                    titulo = vaga.find('h3', class_='base-search-card__title').text.strip()
                    empresa = vaga.find('h4', class_='base-search-card__subtitle').text.strip()
                    local = vaga.find('span', class_='job-search-card__location').text.strip()
                    link_tag = vaga.find_previous('a', class_='base-card__full-link')
                    link = link_tag['href'] if link_tag else "Link indisponivel"
                    todas_vagas.append({"titulo": titulo, "empresa": empresa, "local": local, "link": link})
                except Exception as e:
                    print(f"Erro ao extrair vaga: {e}")

        except Exception as e:
            print(f"Erro ao acessar URL: {e}")

    print(f"Total de vagas coletadas: {len(todas_vagas)}")

    if not todas_vagas:
        enviar_mensagem_telegram("Nenhuma vaga encontrada nesta rodada.")
        return

    notas = avaliar_vagas_gemini(todas_vagas)
    print(f"Notas recebidas: {notas}")

    vagas_enviadas = 0
    for i, vaga in enumerate(todas_vagas):
        nota = notas.get(i+1, 0)
        print(f"[{nota}/10] {vaga['titulo']} | {vaga['empresa']}")
        if nota >= 7:
            mensagem = (
                f"Nova Vaga - Nota {nota}/10\n\n"
                f"Cargo: {vaga['titulo']}\n"
                f"Empresa: {vaga['empresa']}\n"
                f"Local: {vaga['local']}\n"
                f"Link: {vaga['link']}"
            )
            enviar_mensagem_telegram(mensagem)
            vagas_enviadas += 1
            time.sleep(1)

    if vagas_enviadas == 0:
        enviar_mensagem_telegram("Nenhuma vaga relevante encontrada nesta rodada.")

    print(f"Finalizado. {vagas_enviadas} vagas enviadas.")

if __name__ == "__main__":
    buscar_vagas()
