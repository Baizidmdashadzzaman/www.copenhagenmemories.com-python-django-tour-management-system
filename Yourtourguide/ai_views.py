
from django.http import JsonResponse
import json
from gradio_client import Client

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

            try:
                client = Client("ashad0167/chatbot-copenhagenmemories-gp2")
                result = client.predict(
                    msg=user_message,
                    api_name="/chat"
                )
                return JsonResponse({'status': 'success', 'response': result})
            except Exception as e:
                 # Fallback/Error handling for Gradio connection
                 print(f"Gradio Error: {e}")
                 return JsonResponse({'status': 'error', 'message': f"AI Service Error: {str(e)}"}, status=500)

        except Exception as e:
            print(f"View Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
