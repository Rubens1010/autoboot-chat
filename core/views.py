from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import random

# Configurando logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializando o modelo e tokenizer
MODEL_NAME = "microsoft/DialoGPT-medium"  # Modelo especializado em diálogos
tokenizer = None
model = None

def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        try:
            logger.info("Iniciando carregamento do tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            logger.info("Tokenizer carregado com sucesso")

            logger.info("Iniciando carregamento do modelo...")
            model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
            model.eval()  # Colocando o modelo em modo de avaliação
            logger.info("Modelo carregado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo: {str(e)}")
            return False
    return True

def generate_response(question):
    try:
        logger.info(f"Gerando resposta para a pergunta: {question}")
        
        # Tokenizando o input
        inputs = tokenizer.encode(question + tokenizer.eos_token, return_tensors="pt")
        
        # Gerando a resposta
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=100,  # Respostas mais curtas e diretas
                pad_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                do_sample=True,
                top_k=100,
                top_p=0.7,
                temperature=0.8
            )
        
        # Decodificando a resposta
        response = tokenizer.decode(outputs[:, inputs.shape[-1]:][0], skip_special_tokens=True)
        
        logger.info("Resposta gerada com sucesso")
        return response
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}")
        return None

def index(request):
    return render(request, 'index.html')

# Simples armazenamento de sessão em memória
sessions = {}

def atendimento_telecom(user_id, message):
    user = sessions.get(user_id, {
        'step': 0,
        'name': '',
        'email': '',
        'service': '',
        'plan': '',
    })

    if user['step'] == 0:
        user['step'] = 1
        sessions[user_id] = user
        return "Olá! Seja bem-vindo ao atendimento da Conecta+. Qual o seu nome?"

    elif user['step'] == 1:
        user['name'] = message
        user['step'] = 2
        sessions[user_id] = user
        return f"Ótimo, {user['name']}! Agora me informe seu e-mail para contato."

    elif user['step'] == 2:
        user['email'] = message
        user['step'] = 3
        sessions[user_id] = user
        return "Você gostaria de contratar: (1) Internet ou (2) Internet + TV?"

    elif user['step'] == 3:
        if "1" in message:
            user['service'] = "Internet"
        elif "2" in message:
            user['service'] = "Internet + TV"
        else:
            return "Por favor, responda com 1 para Internet ou 2 para Internet + TV."
        user['step'] = 4
        sessions[user_id] = user
        return "Temos: Plano 1 - 200Mb por R$99, Plano 2 - 500Mb + TV por R$149. Qual você escolhe?"

    elif user['step'] == 4:
        if "1" in message:
            user['plan'] = "Plano 1 - 200Mb por R$99"
        elif "2" in message:
            user['plan'] = "Plano 2 - 500Mb + TV por R$149"
        else:
            return "Escolha 1 ou 2 para selecionar um plano."
        user['step'] = 5
        sessions[user_id] = user
        return (f"Confirmando seus dados:\n"
                f"Nome: {user['name']}\n"
                f"E-mail: {user['email']}\n"
                f"Serviço: {user['service']}\n"
                f"Plano: {user['plan']}\n"
                f"Posso finalizar o pedido? (Sim ou Não)")

    elif user['step'] == 5:
        if "sim" in message.lower():
            user['step'] = 6
            sessions[user_id] = user
            return "Pedido finalizado com sucesso! Em breve entraremos em contato. Seu protocolo é: #CON123456"
        else:
            return "Tudo bem. Me avise como posso te ajudar ou se deseja alterar algum dado."

    return "Desculpe, não entendi. Pode repetir por favor?"




# Palavras-chave para detectar perda de intenção
desistencias_keywords = {
    "vou pensar": ["vou pensar", "preciso pensar", "pensar melhor"],
    "muito caro": ["muito caro", "tá caro", "caro demais", "não cabe no meu orçamento"],
    "não quero mais": ["não quero mais", "desisti", "não quero", "cansei"],
    "depois eu vejo": ["depois eu vejo", "vejo depois", "mais tarde", "agora não"]
}

mensagens_reativacao = {
    "vou pensar": [
        "💭 Entendo, mas só hoje temos um cupom exclusivo: **QUERO10**. Válido até às 23:59! 😄",
        "🔔 Posso te lembrar mais tarde com uma oferta personalizada? Assim você não perde essa chance!",
        "🤝 Se tiver alguma dúvida, posso te ajudar a decidir. Estou aqui!"
    ],
    "muito caro": [
        "💸 Sabia que parcelamos em até 12x sem juros? E temos frete grátis hoje!",
        "🎁 Para você, consigo liberar um cupom de 10% OFF agora mesmo! Quer aproveitar?",
        "📉 Que tal darmos uma olhada em opções mais em conta, mas com a mesma qualidade?"
    ],
    "não quero mais": [
        "😌 Tudo bem, mas posso entender melhor o que fez você desistir? Talvez tenha algo que resolva isso.",
        "✨ Sem problemas! Mas antes de sair, posso te mostrar algo que pode te surpreender?",
        "🙏 Só uma última pergunta: tem algo que possamos melhorar para você mudar de ideia?"
    ],
    "depois eu vejo": [
        "🕒 Claro! Posso te mandar um lembrete mais tarde com uma oferta especial?",
        "⏳ Sem pressa, mas só até hoje temos frete grátis + brinde exclusivo!",
        "😉 Que tal garantir agora e cancelar depois, caso mude de ideia? Assim não perde a promoção."
    ]
}

def detectar_motivo_desistencia(frase):
    frase = frase.lower()
    for motivo, palavras in desistencias_keywords.items():
        if any(p in frase for p in palavras):
            return motivo
    return None

def mensagem_reativa_aleatoria(motivo):
    if motivo in mensagens_reativacao:
        return random.choice(mensagens_reativacao[motivo])
    return None


@csrf_exempt
@csrf_exempt
def ask(request):
    if request.method == 'POST':
        try:
            logger.info("Recebendo requisição POST em /api/ask")
            data = json.loads(request.body)
            question = data.get('question', '')
            user_id = request.META.get('REMOTE_ADDR')  # ou use sessão real se desejar

            if not question:
                logger.warning("Pergunta não fornecida")
                return JsonResponse({'error': 'Pergunta não fornecida.'}, status=400)

            # 🔁 Roteiro de atendimento de telecom
            logger.info("Verificando se está em atendimento de telecom")
            if user_id in sessions or "oi" in question.lower() or "quero contratar" in question.lower():
                resposta = atendimento_telecom(user_id, question)
                return JsonResponse({'answer': resposta})

            # 🤖 Detectando intenção de desistência
            motivo = detectar_motivo_desistencia(question)
            if motivo:
                logger.info(f"Desistência detectada: {motivo}")
                resposta_reativa = mensagem_reativa_aleatoria(motivo)
                if resposta_reativa:
                    return JsonResponse({'answer': resposta_reativa})

            # 🤖 Carregar o modelo se necessário
            logger.info("Verificando se o modelo está carregado")
            if not load_model():
                logger.error("Falha ao carregar o modelo")
                return JsonResponse({'error': 'Erro ao carregar o modelo DialoGPT.'}, status=500)

            # 🤖 Gerar resposta genérica
            logger.info("Iniciando geração de resposta")
            answer = generate_response(question)
            if answer is None:
                return JsonResponse({'error': 'Erro ao gerar resposta.'}, status=500)

            return JsonResponse({'answer': answer})

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'JSON inválido.'}, status=400)
        except Exception as e:
            logger.error(f"Erro não tratado: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)
