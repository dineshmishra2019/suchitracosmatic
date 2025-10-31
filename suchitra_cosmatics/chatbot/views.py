import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .rag_chain import rag_app

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            question = data.get("question")

            if not question:
                return JsonResponse({"error": "Question not provided"}, status=400)

            # Use the RAG application
            inputs = {"question": question}
            final_state = await rag_app.ainvoke(inputs)
            
            response_text = final_state.get("generation", "I'm sorry, I couldn't find an answer for that.")

            return JsonResponse({"answer": response_text})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
