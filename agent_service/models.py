
from django.db import models

class UserProfile(models.Model):
    """Représente le profil client soumis à l'Agent."""
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    sector = models.CharField(max_length=100)
    need_description = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.sector}"

class Recommendation(models.Model):
    """Stocke la réponse structurée générée par l'Agent IA."""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=50)
    justification_courte = models.TextField()
    score_confiance = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommandation pour {self.profile.name}"
