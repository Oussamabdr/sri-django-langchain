from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render

from .serializers import ProfileInputSerializer, RecommendationOutputSerializer
from .groq_agent import recommend_product
from .models import UserProfile, Recommendation


# ==========================================================
# API REST
# ==========================================================

class AgentAnalyzeAPIView(APIView):

    def post(self, request, *args, **kwargs):

        input_serializer = ProfileInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                input_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = input_serializer.validated_data

        try:
            recommendation = recommend_product(
                age=data["age"],
                sector=data["sector"],
                need=data["need_description"]
            )

            CONFIDENCE_THRESHOLD = 0.75

            if recommendation.score_confiance < CONFIDENCE_THRESHOLD:
                hitl_status = "À_VALIDER_MANUEL"
                http_status = status.HTTP_202_ACCEPTED
            else:
                hitl_status = "VALIDÉ_AUTO"
                http_status = status.HTTP_200_OK

            response_data = recommendation.model_dump()
            response_data["hitl_status"] = hitl_status

            output_serializer = RecommendationOutputSerializer(data=response_data)
            output_serializer.is_valid(raise_exception=True)

            return Response(output_serializer.data, status=http_status)

        except Exception as e:
            return Response(
                {
                    "error": "Erreur interne du service.",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================================
# INTERFACE WEB
# ==========================================================

def recommendation_form(request):

    # ------------------------------
    # Traitement du formulaire
    # ------------------------------
    if request.method == "POST":

        try:
            profile_data = {
                "name": request.POST.get("name", "Client"),
                "age": int(request.POST.get("age", 0)),
                "sector": request.POST.get("sector", ""),
                "need_description": request.POST.get("need_description", "")
            }

            recommendation = recommend_product(
                age=profile_data["age"],
                sector=profile_data["sector"],
                need=profile_data["need_description"]
            )

            CONFIDENCE_THRESHOLD = 0.75
            result = recommendation.model_dump()

            if result["score_confiance"] < CONFIDENCE_THRESHOLD:
                result["hitl_status"] = "À VALIDER MANUELLEMENT"
            else:
                result["hitl_status"] = "VALIDÉ AUTOMATIQUEMENT"

            result["client_name"] = profile_data["name"]

            # ------------------------------
            # Sauvegarde en base
            # ------------------------------
            profile = UserProfile.objects.create(**profile_data)

            Recommendation.objects.create(
                profile=profile,
                product_id=result["product_id"],
                justification_courte=result["justification_courte"],
                score_confiance=result["score_confiance"]
            )

            return render(request, "agent_service/result.html", {"result": result})

        except Exception as e:
            context = {
                "error": "⚠️ Une erreur est survenue lors de l'analyse. Vérifiez votre connexion ou la clé API.",
                "detail": str(e)
            }
            return render(request, "agent_service/form.html", context)

    # ------------------------------
    # Affichage initial
    # ------------------------------
    return render(request, "agent_service/form.html")


# ==========================================================
# HISTORIQUE
# ==========================================================

def history_view(request):
    history = Recommendation.objects.select_related("profile").order_by("-created_at")
    return render(request, "agent_service/history.html", {"history": history})
