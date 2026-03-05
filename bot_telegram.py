import os
import requests
from dotenv import load_dotenv

# Isso aqui abre o seu arquivo .env e carrega as variáveis para a memória
load_dotenv()

# Puxando as senhas do cofre
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_mensagem_telegram(mensagem):
    # Essa é a URL oficial do Telegram para o seu bot
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # O pacote de dados que vamos enviar
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem
    }
    
    # Enviando a requisição para a internet
    resposta = requests.post(url, json=payload)
    
    # Verificando se o Telegram aceitou
    if resposta.status_code == 200:
        print("✅ Sucesso! Olhe o seu celular.")
    else:
        print(f"❌ Algo deu errado. Erro: {resposta.text}")

# Testando o nosso bot na prática
if __name__ == "__main__":
    texto_teste = "Fala Pedro! Seu bot tá online, configurado com boas práticas e pronto para caçar as melhores vagas de Engenheiro de IA pelo Rio de Janeiro! 🚀"
    enviar_mensagem_telegram(texto_teste)
