import re

def detect_red_flags_debug(patient_case: str, answers: list) -> list:
    combined_text = (patient_case + " " + " ".join(answers)).lower()
    combined_text = combined_text.replace("’", "'").replace("`", "'")
    
    print(f"DEBUG combined_text: '{combined_text}'")
    
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
        ]
    }
    
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
    
    detected = []
    for flag, patterns in red_flag_definitions.items():
        for pattern in patterns:
            matches = list(re.finditer(pattern, combined_text))
            for match in matches:
                start_idx = max(0, match.start() - 35)
                preceding_text = combined_text[start_idx:match.start()]
                print(f"DEBUG match found: '{match.group()}' at {match.start()}")
                print(f"DEBUG preceding_text (35 chars): '{preceding_text}'")
                negation_found = re.search(negation_pattern, preceding_text)
                print(f"DEBUG negation search in preceding_text: {negation_found}")
                if negation_found:
                    print(f"DEBUG negation matched: '{negation_found.group()}'")
                has_punctuation = any(p in preceding_text for p in [".", ";"])
                print(f"DEBUG has_punctuation: {has_punctuation}")
                
                if negation_found and not has_punctuation:
                    print("DEBUG => IGNORED (negated)")
                    continue
                else:
                    print("DEBUG => DETECTED")
                    detected.append(flag)
                    break
    return detected

# Scenario 1 text
case1 = "Patient avec toux légère, nez qui coule, fatigue modérée depuis 2 jours."
ans1 = [
    "Depuis 2 jours précisément.",
    "Pas de fièvre constatée.",
    "Une fatigue légère mais pas de douleur ni gêne respiratoire.",
    "Pas d'antécédents particuliers ni de traitement.",
    "Non, pas d'aggravation rapide."
]

print("--- RUNNING SCENARIO 1 DEBUG ---")
res1 = detect_red_flags_debug(case1, ans1)
print(f"Scenario 1 Red Flags: {res1}\n")

# Scenario 3 text
case3 = "Patient avec fatigue légère après effort physique intense, sans fièvre ni douleur."
ans3 = [
    "Depuis la fin de ma course hier après-midi.",
    "Non, pas de fièvre.",
    "Seulement de la fatigue, aucune gêne respiratoire.",
    "Aucun antécédent médical.",
    "Non, la fatigue s'estompe progressivement."
]

print("--- RUNNING SCENARIO 3 DEBUG ---")
res3 = detect_red_flags_debug(case3, ans3)
print(f"Scenario 3 Red Flags: {res3}\n")
