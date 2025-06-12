from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

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

@csrf_exempt
def ask(request):
    if request.method == 'POST':
        try:
            logger.info("Recebendo requisição POST em /api/ask")
            data = json.loads(request.body)
            question = data.get('question', '')
            
            if not question:
                logger.warning("Pergunta não fornecida")
                return JsonResponse({'error': 'Pergunta não fornecida.'}, status=400)
            
            # Carregando o modelo se ainda não estiver carregado
            logger.info("Verificando se o modelo está carregado")
            if not load_model():
                logger.error("Falha ao carregar o modelo")
                return JsonResponse({'error': 'Erro ao carregar o modelo DialoGPT.'}, status=500)
            
            # Gerando a resposta
            logger.info("Iniciando geração de resposta")
            answer = generate_response(question)
            
            if answer is None:
                logger.error("Falha ao gerar resposta")
                return JsonResponse({'error': 'Erro ao gerar resposta.'}, status=500)
            
            logger.info("Resposta enviada com sucesso")
            return JsonResponse({'answer': answer})
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {str(e)}")
            return JsonResponse({'error': 'JSON inválido.'}, status=400)
        except Exception as e:
            logger.error(f"Erro não tratado: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    logger.warning("Método não permitido")
    return JsonResponse({'error': 'Método não permitido.'}, status=405)
