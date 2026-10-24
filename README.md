# Système Multi-Agents Médical avec LangGraph

Cette application académique simule un workflow d'orientation clinique préliminaire et de synthèse médicale grâce à un système multi-agents orchestré par **LangGraph**, exposé via une API **FastAPI**, connecté à un frontend **Streamlit** et intégré avec un serveur **MCP (Model Context Protocol)** autonome.

---

## ⚠️ Avertissement Éthique et Légal (Obligatoire)

> [!WARNING]
> **Ce projet est strictement académique et pédagogique.**
> - Il ne doit jamais être présenté ni utilisé comme un véritable dispositif médical.
> - L'application ne produit aucun diagnostic définitif.
> - Elle formule uniquement une orientation clinique préliminaire, une synthèse clinique factuelle et une recommandation intermédiaire prudente.
> - Le rapport d'orientation final contient obligatoirement la phrase : **"Ce système ne remplace pas une consultation médicale."**

---

## Architecture du Projet

Le projet respecte la structure suivante :

```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── graph.py
│   │   ├── api.py
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── supervisor.py
│   │   │   ├── diagnostic_agent.py
│   │   │   ├── physician_review.py
│   │   │   └── report_agent.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── patient_tools.py
│   │   │   ├── care_tools.py
│   │   │   └── mcp_client.py
│   │   └── storage/
│   │       ├── __init__.py
│   │       └── memory_store.py
│   ├── requirements.txt
│   ├── langgraph.json
│   └── .env.example
├── mcp_server/
│   ├── server.py
│   └── data/
├── frontend/
│   ├── app.py
│   └── requirements.txt
├── README.md
└── tests/
    ├── test_graph.py
    ├── test_api.py
    └── test_scenarios.py
```

---

## Installation et Lancement

### 1. Configuration des variables d'environnement
Créez un fichier `.env` dans le dossier `backend/` à partir de `backend/.env.example` :
```bash
cp backend/.env.example backend/.env
```
Renseignez votre clé API OpenAI si vous souhaitez utiliser l'IA générative (sinon, l'application basculera automatiquement sur un mode local déterministe avec templates cliniques de haute qualité) :
```env
OPENAI_API_KEY=votre_cle_api_ici
MCP_SERVER_URL=http://localhost:23000/sse
```

---

### 2. Démarrage du Serveur MCP

Le serveur MCP fournit des directives cliniques globales basées sur les symptômes. Il utilise le protocole SSE sur le port 23000.

```bash
cd mcp_server
pip install mcp
python server.py
```

---

### 3. Démarrage du Backend (FastAPI)

Le backend héberge le graphe d'agents LangGraph et expose l'API REST.

```bash
cd backend
pip install -r requirements.txt
uvicorn app.api:app --reload --port 8000
```
L'API sera accessible sur `http://localhost:8000`. Vous pouvez consulter sa documentation interactive sur `http://localhost:8000/docs`.

---

### 4. Démarrage du Graphe dans LangGraph Studio (Optionnel)

Pour visualiser et interagir avec le graphe graphiquement :
```bash
cd backend
langgraph dev
```

---

### 5. Démarrage du Frontend (Streamlit)

Le frontend offre une interface web premium pour piloter la consultation.

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
L'interface s'ouvrira automatiquement à l'adresse `http://localhost:8501`.

---

## Scénarios de Test

L'application intègre 3 scénarios typiques directement sélectionnables sur l'Écran 1 pour tester le workflow de bout en bout :

1. **Cas 1 : Syndrome respiratoire bénin**
   - *Description :* "Patient avec toux légère, nez qui coule, fatigue modérée depuis 2 jours."
   - *Comportement :* Le graphe pose les 5 questions successives, ne détecte pas d'alerte grave (red flags vides), formule des conseils généraux de repos/hydratation, passe en revue médecin, et génère le rapport final après validation médicale.
   
2. **Cas 2 : Cas grave (Red Flags)**
   - *Description :* "Patient avec douleur thoracique, difficulté respiratoire et fièvre élevée."
   - *Comportement :* Détecte les signes d'alerte "douleur thoracique" et "difficulté respiratoire", formule une recommandation immédiate d'orientation vers les urgences, et soumet le dossier au médecin.
   
3. **Cas 3 : Fatigue bénigne d'effort**
   - *Description :* "Patient avec fatigue légère après effort physique intense, sans fièvre ni douleur."
   - *Comportement :* Pas d'alertes cliniques, recommandations de repos courantes, et édition directe du rapport final après saisie du médecin.

---

## Exécution des Tests Automatisés

Vous pouvez valider le bon fonctionnement de toute la logique et des scénarios via Pytest :
```bash
# Depuis la racine du projet
pytest tests/
```

---

## Limites du Système
- Ce système n'effectue aucun diagnostic médical et n'a pas vocation à se substituer aux professionnels de santé.
- Les réponses et l'orientation dépendent exclusivement des déclarations du patient.
- Toute aggravation de symptômes doit donner lieu à un appel au 15 (ou 112) ou à une consultation auprès d'un médecin.
