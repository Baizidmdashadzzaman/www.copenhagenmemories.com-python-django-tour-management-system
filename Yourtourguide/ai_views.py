
import os
import re
import json
import torch
from django.conf import settings
from django.http import JsonResponse
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Cache for the pipeline to avoid reloading the model on every request
_chatbot_pipeline = None

def get_chatbot_pipeline():
    global _chatbot_pipeline
    if _chatbot_pipeline is None:
        model_path = os.path.join(settings.BASE_DIR, 'trained-models', 'model')
        
        # Load the tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        # Load the causal language model
        model = AutoModelForCausalLM.from_pretrained(model_path)
        
        # Determine the execution device (GPU if available, otherwise CPU)
        device = 0 if torch.cuda.is_available() else -1
        
        # Instantiate the pipeline
        _chatbot_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=device
        )
    return _chatbot_pipeline

common_typos = {
    "somting": "something",
    "mch": "much",
    "plz": "please",
    "teh": "the",
    "recieve": "receive",
    "adress": "address",
    "tommorow": "tomorrow",
    "wht": "what",
    "cant": "can't",
    "dont": "don't",
}

def normalize_question(text):
    normalized = text.lower()
    for typo, correct in common_typos.items():
        normalized = re.sub(rf"\b{re.escape(typo)}\b", correct, normalized)
    return normalized

def ai_chat_proxy(request):
    if request.method == 'POST':
        try:
            # Handle both JSON body and form-urlencoded
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                user_message = data.get('message')
            else:
                user_message = request.POST.get('message')
            
            if not user_message:
                return JsonResponse({'status': 'error', 'message': 'No message provided'}, status=400)

            # Normalize the input message to correct common typos
            normalized_message = normalize_question(user_message)
            
            # Format prompt matching the dataset's combine_text format
            prompt = f"User: {normalized_message}\nCopenhagenMemories:"
            
            chatbot = get_chatbot_pipeline()
            response = chatbot(
                prompt,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                pad_token_id=chatbot.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            
            # Extract response text
            if "CopenhagenMemories:" in generated_text:
                result = generated_text.split("CopenhagenMemories:")[-1].strip()
            else:
                result = generated_text.replace(prompt, "").strip()
                
            return JsonResponse({'status': 'success', 'response': result})

        except Exception as e:
            print(f"Chatbot Error: {e}")
            return JsonResponse({'status': 'error', 'message': f"AI Service Error: {str(e)}"}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

