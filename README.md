# Chatbot com LLaMA 2

Este é um chatbot web interativo que utiliza o modelo LLaMA 2 para processar perguntas dos usuários, implementado com Python, Django e Bootstrap.

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Ambiente virtual Python (recomendado)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd [NOME_DO_DIRETÓRIO]
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações:
```bash
python manage.py migrate
```

5. Inicie o servidor:
```bash
python manage.py runserver
```

## Uso

1. Acesse `http://localhost:8000` no seu navegador
2. Digite sua pergunta no campo de texto
3. Clique em "Enviar" ou pressione Enter
4. Aguarde a resposta do chatbot

## Estrutura do Projeto

```
chatbot/
├── manage.py
├── requirements.txt
├── chatbot/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/
    ├── __init__.py
    ├── views.py
    ├── urls.py
    ├── templates/
    │   └── index.html
    └── static/
        ├── css/
        │   └── custom.css
        └── js/
            └── chatbot.js
```

## Tecnologias Utilizadas

- Django 5.0.2
- LLaMA 2 (via transformers)
- Bootstrap 5
- JavaScript (Vanilla) 