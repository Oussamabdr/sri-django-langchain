from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# --------------------------------------------------
# Chargement de la clé API
# --------------------------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("La clé GROQ_API_KEY n'est pas configurée.")

# --------------------------------------------------
# Schéma Pydantic
# --------------------------------------------------
class RecommendationSchema(BaseModel):
    product_id: str = Field(description="ID du produit recommandé")
    justification_courte: str = Field(description="Justification courte")
    score_confiance: float = Field(description="Score entre 0 et 1")

# --------------------------------------------------
# Parser et LLM
# --------------------------------------------------
parser = PydanticOutputParser(pydantic_object=RecommendationSchema)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.1
)

# --------------------------------------------------
# Création de la chaîne
# --------------------------------------------------
def generate_recommendation_chain():

    template = """
Tu es un expert en recommandation de produits B2B.
Analyse le profil client et recommande un seul produit.

Produits disponibles :
- S-2024-PRO : Analyse avancée de données.
- B-2024-ESS : Gestion basique.
- C-2024-MIG : Migration cloud.

Profil client :
- Âge : {age}
- Secteur : {sector}
- Besoin : {need}

{format_instructions}
"""

    prompt = ChatPromptTemplate.from_template(
        template,
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    return prompt | llm | parser

# --------------------------------------------------
# Fonction principale
# --------------------------------------------------
def recommend_product(age: int, sector: str, need: str):

    try:
        chain = generate_recommendation_chain()
        result = chain.invoke({
            "age": age,
            "sector": sector,
            "need": need
        })
        return result

    except Exception as e:
        print("Erreur LLM :", e)
        return RecommendationSchema(
            product_id="ERROR",
            justification_courte=str(e),
            score_confiance=0.0
        )
