🤖 Radar de Vagas de IA - Engenharia de ML & Deep Learning
Este projeto é um bot automatizado que monitora o LinkedIn em busca das melhores oportunidades na área de Inteligência Artificial, com foco especial em Engenharia de Machine Learning, Deep Learning e Redes Neurais.

O objetivo é garantir que nenhuma vaga relevante seja perdida, enviando alertas em tempo real diretamente para o Telegram.

🚀 Funcionalidades
Busca em Tempo Real: Monitora vagas postadas nos últimos 90 minutos para garantir rapidez na candidatura.

Filtro Geográfico Inteligente: Seleciona apenas vagas Remotas ou localizadas no Rio de Janeiro.

Cérebro de Machine Learning: Utiliza a biblioteca scikit-learn para analisar o título da vaga e decidir se ela realmente bate com o perfil de IA desejado, evitando falsos positivos.

Automação Total: Configurado para rodar 24 horas por dia, de hora em hora, utilizando GitHub Actions.

🛠️ Tecnologias Utilizadas
Python: Linguagem base do projeto.

BeautifulSoup4: Para a raspagem de dados (web scraping) do LinkedIn.

scikit-learn: Para a inteligência de classificação e filtragem das vagas.

Telegram Bot API: Para o envio das notificações instantâneas.

GitHub Actions: Para a automação e execução na nuvem.

📂 Estrutura do Projeto
olheiro.py: O script principal que realiza a busca e aplica os filtros de ML.

bot_telegram.py: Módulo responsável pela comunicação com a API do Telegram.

monitor.yml: Configuração da automação para rodar de hora em hora.

.env: Arquivo (protegido) contendo as chaves de acesso.

⚙️ Como Executar
Clone o repositório.

Crie um ambiente virtual: python -m venv venv.

Instale as dependências: pip install -r requirements.txt.

Configure suas variáveis de ambiente no arquivo .env (Token do Telegram e Chat ID).

Execute o script: python olheiro.py.
