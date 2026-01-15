from rest_framework import serializers
from .groq_agent import RecommendationSchema

# Sérialiseur pour les données d'entrée (Profil Client)
class ProfileInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18)
    sector = serializers.CharField(max_length=100)
    need_description = serializers.CharField(max_length=500)

# Sérialiseur pour les données de sortie (RecommendationSchema)
# Nous utilisons un sérialiseur basé sur la classe Pydantic pour garantir le format
class RecommendationOutputSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    justification_courte = serializers.CharField()
    score_confiance = serializers.FloatField()

    # Méthode pour créer le sérialiseur directement à partir d'un objet Pydantic
    @classmethod
    def from_pydantic(cls, pydantic_obj: RecommendationSchema):
        return cls(pydantic_obj.model_dump())
