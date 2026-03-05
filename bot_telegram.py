import os
import requests
from dotenv import load_dotenv

# Tenta ler o .env no seu PC. No GitHub ele vai ler os Secrets do site.
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_mensagem_telegram(mensagem):
    # Debug para saber se as chaves chegaram na nuvem
    if not TOKEN or not CHAT_ID:
        print("DEBUG Erro: Token ou Chat ID nao encontrados no sistema.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    
    try:
        resposta = requests.post(url, json=payload)
        if resposta.status_code != 200:
            print(f"Erro no Telegram: {resposta.text}")
    except Exception as e:
        print(f"Erro ao conectar com o Telegram: {e}")
