import re
from typing import List, Optional

# Liste ordonnée des 5 questions successives
QUESTIONS = [
    "Depuis quand avez-vous ces symptômes ?",
    "Avez-vous de la fièvre ? Si oui, quelle température ?",
    "Ressentez-vous une douleur, une gêne respiratoire ou une fatigue importante ?",
    "Avez-vous des antécédents médicaux ou prenez-vous un traitement ?",
    "Les symptômes s’aggravent-ils ou avez-vous remarqué des signes inquiétants ?"
]

def get_next_question(question_count: int, patient_case: str, answers: List[str]) -> Optional[str]:
    """Retourne la prochaine question adaptée basée sur le nombre actuel de questions posées."""
    if 0 <= question_count < len(QUESTIONS):
        return QUESTIONS[question_count]
    return None

def detect_red_flags(patient_case: str, answers: List[str]) -> List[str]:
    """Détecte les signes inquiétants (red flags) dans le cas initial et les réponses du patient.
    
    Prend en compte les négations pour éviter les faux positifs (ex: 'aucune gêne respiratoire').
    """
    combined_text = (patient_case + " " + " ".join(answers)).lower()
    
    # Remplacer les apostrophes pour simplifier les expressions régulières
    combined_text = combined_text.replace("’", "'").replace("`", "'")
    
    detected = []
    
    # Dictionnaire des regex de mots-clés par red flag
    red_flag_definitions = {
        "difficulté respiratoire": [
            r"gêne(s)? respiratoire(s)?",
            r"difficulté(s)? respiratoire(s)?",
            r"respiration difficile",
            r"essoufflement",
            r"étouffement",
            r"dyspnée",
            r"mal à respirer",
            r"difficulté à respirer"
        ],
        "douleur thoracique": [
            r"douleur(s)? thoracique(s)?",
            r"douleur(s)? (à la poitrine|poitrine)",
            r"oppression(s)? thoracique(s)?",
            r"poitrine serrée",
            r"mal au thorax",
            r"douleur(s)? oppressive(s)?"
        ],
        "perte de connaissance": [
            r"perte(s)? de connaissance",
            r"évanouissement",
            r"syncope",
            r"perdu connaissance",
            r"tombé(e)? dans les pommes",
            r"inconscient"
        ],
        "aggravation rapide": [
            r"aggravation rapide",
            r"aggrave(nt)? rapidement",
            r"empire(nt)? rapidement",
            r"pire en pire"
        ],
        "douleur intense": [
            r"douleur(s)? intense(s)?",
            r"douleur(s)? insupportable(s)?",
            r"douleur(s)? violente(s)?",
            r"douleur(s)? très vive(s)?",
            r"douleur(s)? aiguë(s)?",
            r"très mal"
        ],
        "confusion": [
            r"confusion",
            r"confus",
            r"désorienté",
            r"délire"
        ],
        "saignement important": [
            r"saignement(s)? important(s)?",
            r"saignement(s)? abondant(s)?",
            r"hémorragie",
            r"crache du sang"
        ]
    }
    
    # Négations courantes pouvant annuler un signe de gravité
    negations = [
        r"pas\s+de",
        r"sans",
        r"aucune(s)?",
        r"aucun(s)?",
        r"pas\s+d'",
        r"ne\s+ressens\s+pas",
        r"ne\s+sens\s+pas",
        r"non"
    ]
    negation_pattern = "|".join(negations)
    
    for flag, patterns in red_flag_definitions.items():
        for pattern in patterns:
            matches = list(re.finditer(pattern, combined_text))
            for match in matches:
                # Regarder si ce match est précédé d'une négation dans les 35 caractères précédents
                start_idx = max(0, match.start() - 35)
                preceding_text = combined_text[start_idx:match.start()]
                
                negation_match = re.search(negation_pattern, preceding_text)
                if negation_match:
                    # Vérifier s'il y a une ponctuation forte entre la négation et le mot-clé
                    text_between = preceding_text[negation_match.end():]
                    if any(p in text_between for p in [".", ";"]):
                        # Il y a une ponctuation intermédiaire, donc la négation ne s'applique pas à ce mot-clé
                        detected.append(flag)
                        break
                    else:
                        # Pas de ponctuation intermédiaire, le signe est bien nié
                        continue
                else:
                    detected.append(flag)
                    break
                    
    # Gestion spécifique de la fièvre très élevée
    fever_patterns = [r"fièvre", r"fievre", r"température", r"temperature"]
    has_fever_kw = any(re.search(pat, combined_text) for pat in fever_patterns)
    
    if has_fever_kw:
        # Trouver des valeurs de température numérique (ex: 39, 39.5, 40)
        temp_matches = re.findall(r'\b(3[894][.,]\d+|40[.,]\d+|41[.,]\d+|39|40|41)\b', combined_text)
        for temp_str in temp_matches:
            try:
                temp_val = float(temp_str.replace(",", "."))
                if temp_val >= 39.0:
                    detected.append("fièvre très élevée")
                    break
            except ValueError:
                pass
                
    return list(set(detected))
