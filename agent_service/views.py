from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Importation des sérialiseurs
from .serializers import ProfileInputSerializer, RecommendationOutputSerializer

# Importation de la fonction de l'Agent (Groq)
from .groq_agent import recommend_product

from django.shortcuts import render

# ==========================================================
# API REST : Endpoint pour analyser un profil client
# ==========================================================

class AgentAnalyzeAPIView(APIView):
    """
    Endpoint API pour soumettre un profil client et recevoir une recommandation.
    Intègre la logique Human-in-the-Loop (HITL) basée sur la confiance.
    """

    def post(self, request, *args, **kwargs):

        # 1. Validation des données d'entrée
        input_serializer = ProfileInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                input_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = input_serializer.validated_data

        # 2. Appel de l'Agent IA (Groq)
        try:
            pydantic_recommendation = recommend_product(
                age=data['age'],
                sector=data['sector'],
                need=data['need_description']
            )

            # -------------------------------------------------
            # LOGIQUE HUMAN-IN-THE-LOOP (HITL)
            # -------------------------------------------------
            CONFIDENCE_THRESHOLD = 0.75

            if pydantic_recommendation.score_confiance < CONFIDENCE_THRESHOLD:
                hitl_status = "À_VALIDER_MANUEL"
                http_status = status.HTTP_202_ACCEPTED
            else:
                hitl_status = "VALIDÉ_AUTO"
                http_status = status.HTTP_200_OK

            # 3. Préparation de la réponse
            response_data = pydantic_recommendation.model_dump()
            response_data['hitl_status'] = hitl_status

            output_serializer = RecommendationOutputSerializer(data=response_data)
            output_serializer.is_valid(raise_exception=True)

            return Response(output_serializer.data, status=http_status)

        except Exception as e:
            return Response(
                {
                    "error": "Erreur interne critique du service d'Agent.",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================================
# INTERFACE WEB : Formulaire utilisateur
# ==========================================================

def recommendation_form(request):
    """
    Gère l'affichage du formulaire et le traitement des données POST.
    """

    # 1. Traitement des données POST
    if request.method == 'POST':

        try:
            profile_data = {
                "name": request.POST.get('name', 'Client Anonyme'),
                "age": int(request.POST.get('age', 0)),
                "sector": request.POST.get('sector', ''),
                "need_description": request.POST.get('need_description', '')
            }
        except ValueError:
            context = {'error': "L'âge doit être un nombre valide."}
            return render(request, 'agent_service/form.html', context)

        # 2. Appel de l'Agent IA
        recommendation = recommend_product(
            age=profile_data['age'],
            sector=profile_data['sector'],
            need=profile_data['need_description']
        )

        # 3. Logique HITL (copie de la logique API)
        CONFIDENCE_THRESHOLD = 0.75
        result = recommendation.model_dump()

        if result['score_confiance'] < CONFIDENCE_THRESHOLD:
            result['hitl_status'] = "À VALIDER MANUELLEMENT"
        else:
            result['hitl_status'] = "VALIDÉ AUTOMATIQUEMENT"

        result['client_name'] = profile_data['name']

        # 4. Affichage du résultat
        return render(request, 'agent_service/result.html', {'result': result})

    # 5. Affichage du formulaire (GET)
    return render(request, 'agent_service/form.html')

