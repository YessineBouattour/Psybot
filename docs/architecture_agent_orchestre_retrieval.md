\[Architecture de l’article

Question Input  
Agent d’orchestre  
Retriever Bank ( Text \+ Graph) Base vectorielle pour les données non structurés (Texte)   
                                                  Graphe pour les données structurés (graphe)  
Generator  
Critic Module  
Réponse

Feedback loop: critic module vers l’agent d’orchestre)\]  
\+++++++++++++++++++++++++++++++++++++++++++++++++++++  
\++++++++++++++++++++++++++++++++++++++++++++++++++++  
Tâches à réaliser: 

- préparation de pipeline de l’article  
- Préparation des bases de données pour chaque Retrieval Bank   
- Stockage des bases de données textuelles dans la BD Quadrant ( BD vectorielle)

\++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
\+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Liens des codes:  
[**https://github.com/snapc-stanford/stark.git**](https://github.com/snap-stanford/stark.git)  
[**https://github.com/HuskyInSalt/CRAG.git**](https://github.com/HuskyInSalt/CRAG.git)

1) Préparation de pipeline de l’article

Architecture Technique:

1) Question (input): embedding (choisir le modéle à utiliser) \=\> BAAI/bge-m3

![][image1]

2) Agent d’orchestre ? : Claude 3 ou Llama3.1 70 B  
- Prend question  
- Extraire le contexte \+ entitées relations sémantiques  
- Output: la liste d’actions en sebasant sur le contexte, entitées, relations

Rq: chaque LLM doit avoir un Prompt (role, ……)  
               \- Prompt ?????

3) Retriever Bank : récupération des informations pour générer la bonne réponse

* Text Retrieval Module  
- STARK , OPEN IA  
- Input: question reformulé donné par l’agent d’orchestre  
- Il faut faire l'étape d’embedding aux documents  
- Output: k documents PDF les plus similaires au question  
- Méthode: vector similarity search ( t9aren vector mte3 query avec vector de chaque document)

  \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

- CRAG: Web Search  
- Output: K pages web


  \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

- Ranker: ???? (Ada…. ou bge ……)

            Donc le **ranker/embedding model** dépend du benchmark :

- **STARK → Ada-002**

- **CRAG → BGE-M3**  
    
- Input de ranker: question \+ documents condidats \+ page web condidats  
- Output: k documents filtrés les plus pertinents   
- Méthode: calcul de similarité simple entre les documents candidats 

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*  
\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

* Graph Retrieval Module: graphe (noeuds= documents / edges= relations entre les documents)  
- STARK RAG:   
- Input: contexte (domaine)/ entitées / relations sémantique  
- Output: document qui contient l’information \+ chemin de raisonnement  
- Méthode:   
* chaque noeud ( fiha Entités relations elli fi question) on va extraire ego\_graph (sous graphe)  
* Ces relations   
* Récupérer les documents associés aux noeuds de sous graphe  
- CRAG:   
- Input: contexte(domaine) / entitées/ relations sémantique)  
- Output: document qui contient l’information \+ chemin de raisonnement  
- Méthode: méme que STARK théorie de graphe basé sur ego graph extraction  
             \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*  
- Ranker:   
- Input de ranker: question \+ sous graphe  
- Output: k relations mel sous graphe  
- Méthode: similarité entre question et ??? graphe


                      

**Pipeline:**

**![][image2]**

**REALISATION**

1. **Question Input & Embedding:  turn text into a numeric vector (embedding)**

   * **Question texte → transformée en vecteur (embedding) pour comparer avec documents et graphes.** 

2. **Agent d’Orchestre (LLM : Claude 3 / LLaMA 3.1 70B)**

   * **Reçoit la question (ou embedding).**

   * **Extrait contexte, entités, relations.**

   * **Génère liste d’actions pour Text Retrieval et Graph Retrieval.** 

3. **Text Retrieval Module (STARK / CRAG)**

   * **Embeddings de documents / pages web.**

   * **Vector similarity search avec embedding de la question.**

   * **Ranker filtre les documents les plus pertinents.** 

4. **Graph Retrieval Module (STARK RAG / CRAG Graph)**

   * **Recherche sur le graphe basé sur contexte, entités, relations.**

   * **Extraction d’ego-graph → documents \+ chemin de raisonnement.**

   * **Graph Ranker filtre les relations les plus pertinentes.** 

5. **Parallélisation**

   * **Text Retrieval et Graph Retrieval peuvent fonctionner en parallèle, car ils utilisent le même input mais des méthodes différentes.** 

6. **Generator**

   * **Combine documents textuels \+ relations du graphe pour générer la réponse finale.** 

7. **Critic Module**

   * **Évalue la réponse et envoie un feedback loop à l’agent d’orchestre pour ajuster la génération.**   
       
       
     **\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\***  
     **\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\***  
     **Etape 1: Agent orchestre: Claude 3 ou LLama**  
* **input= question \+ \+ \+**   
* **Tâches: extraction de domaine / extraction des entitées/ types de relations disponibles/ selection (texte recherche ou graphe recherche)**   
* **Génération du plan de travail : (D, E, R, S)**  
* **Prompt : …..**

  **Code premier dossier**

**Fichier 1: agent\_step\_1.py**

**"""**

**Implémentation de l'Étape 1: AGENT pour AGENT-G (Version SANS ontologie)**

**Ce script définit la classe Agent, qui utilise un LLM (Claude 3 Sonnet)**

**pour décomposer une question \+ feedback en une action structurée (Action a\_t).**

**Cette version ne prend PAS de liste d'entités ou de relations en entrée.**

**L'agent doit deviner les types lui-même.**

**"""**

**import os**

**import json**

**import anthropic**

**from typing import List, Optional**

**from pydantic import BaseModel, Field, field\_validator**

**\# \--- 1\. Définition des Structures de Données (Pydantic) \---**

**class EntiteExtraite(BaseModel):**

    **"""**

    **Structure pour une entité extraite.**

    **Le type sera deviné par le LLM.**

    **"""**

    **name: str \= Field(..., description="Le nom de l'entité extraite, ex: 'John Smith'")**

    **type: str \= Field(..., description="Le type deviné de l'entité, ex: 'Auteur', 'Sujet'")**

**class Action(BaseModel):**

    **"""**

    **Définit la structure de sortie "Action a\_t"**

    **que l'Agent doit produire.**

    **"""**

    **domaine: str \= Field(..., description="Le domaine de la question, ex: 'Science des matériaux'")**

    **entites: List\[EntiteExtraite\] \= Field(..., description="Liste des entités extraites")**

    **relations: List\[str\] \= Field(..., description="Liste des relations d'intérêt devinées")**

    **selection\_module: str \= Field(..., description="Module à utiliser: 'text' ou 'graph'")**

    **@field\_validator('selection\_module')**

    **def validate\_selection\_module(cls, v):**

        **"""Valide que la sélection est soit 'text' soit 'graph'."""**

        **if v not in \['text', 'graph'\]:**

            **raise ValueError("selection\_module doit être 'text' ou 'graph'")**

        **return v**

**\# \--- 2\. Configuration du Client API \---**

**try:**

    **client \= anthropic.Anthropic(api\_key=os.environ\["ANTHROPIC\_API\_KEY"\])**

    **MODEL\_NAME \= "claude-3-sonnet-20240229"**

**except anthropic.AuthenticationError:**

    **print("Erreur: La variable d'environnement ANTHROPIC\_API\_KEY n'est pas définie.")**

    **client \= None**

**\# \--- 3\. Construction du Prompt Système \---**

**def \_build\_system\_prompt() \-\> str:**

    **"""**

    **Construit le prompt système pour guider l'Agent LLM.**

    **(Version SANS listes d'ontologie)**

    **"""**

    **return f"""**

**Tu es AGENT-G, un agent expert en prise de décision.**

**Ton rôle est l'Étape 1: analyser la question d'un utilisateur et un feedback optionnel,**

**puis générer un plan d'action structuré.**

**Tu dois effectuer les tâches suivantes:**

**1\.  \*\*Extraction du domaine (d\_t)\*\*: Identifie le sujet principal.**

**2\.  \*\*Extraction des entités (E\_t)\*\*: Extrais les entités CLÉS de la question** 

    **et devine leur type (ex: 'Personne', 'Lieu', 'Sujet').**

**3\.  \*\*Extraction des relations (R\_t)\*\*: Identifie les relations d'intérêt** 

    **(ex: 'publié par', 'situé à').**

**4\.  \*\*Sélection du module (s\_t)\*\*: Choisis 'graph' ou 'text'.**

**RÈGLES IMPORTANTES :**

**1\.  \*\*SÉLECTION DU MODULE\*\*:**

    **\- Utilise 'graph' si la question concerne des relations spécifiques** 

      **entre des entités claires.**

    **\- Utilise 'text' si la question est factuelle, ouverte, ou si les**

      **entités sont des concepts abstraits.**

**2\.  \*\*FORMAT DE SORTIE\*\* :**

    **Tu DOIS répondre UNIQUEMENT avec un objet JSON valide**

    **correspondant à cette structure. N'ajoute aucun texte avant ou**

    **après le JSON.**

    **Format JSON attendu (basé sur Action a\_t):**

    **{{**

      **"domaine": "...",**

      **"entites": \[**

        **{{"name": "...", "type": "..."}}**

      **\],**

      **"relations": \["..."\],**

      **"selection\_module": "text|graph"**

    **}}**

**"""**

**\# \--- 4\. Logique de l'Agent (Étape 1\) \---**

**def run\_agent\_step\_1(**

    **question: str,** 

    **feedback: Optional\[str\] \= None**

**) \-\> Optional\[Action\]:**

    **"""**

    **Exécute l'Étape 1: Prise de décision de l'AGENT.**

    **Inputs:**

    **\- question (q)**

    **\- feedback (f\_{t-1})**

    **"""**

    

    **if not client:**

        **print("Le client API n'est pas initialisé.")**

        **return None**

    **\# 1\. Construire le prompt système (sans arguments)**

    **system\_prompt \= \_build\_system\_prompt()**

    

    **\# 2\. Construire le message utilisateur**

    **user\_message \= f"Question de l'utilisateur:\\n{question}\\n"**

    

    **if feedback:**

        **user\_message \+= f"""**

**Feedback de l'itération précédente:**

**{feedback}**

**Tu DOIS corriger ton plan en te basant sur ce feedback.**

**"""**

    

    **messages \= \[**

        **\# Ici, vous ajouteriez vos exemples ICL (In-Context Learning)**

        **\# qui seraient aussi "sans ontologie"**

        **{"role": "user", "content": user\_message}**

    **\]**

    **\# 4\. Appeler l'API Claude**

    **try:**

        **print(f"--- Appel de l'Agent (Modèle: {MODEL\_NAME}) \---")**

        **response \= client.messages.create(**

            **model=MODEL\_NAME,**

            **max\_tokens=1024,**

            **temperature=0.0,**

            **system=system\_prompt,**

            **messages=messages**

        **)**

        

        **\# 5\. Extraire, Parser et Valider la réponse**

        **json\_output \= response.content\[0\].text**

        

        **if json\_output.strip().startswith("\`\`\`json"):**

            **json\_output \= json\_output.strip()\[7:-3\].strip()**

        

        **data \= json.loads(json\_output)**

        **action\_plan \= Action(\*\*data) \# Validation Pydantic**

        

        **return action\_plan**

    **except anthropic.APIError as e:**

        **print(f"Erreur API Anthropic: {e}")**

    **except json.JSONDecodeError as e:**

        **print(f"Erreur: Le LLM n'a pas retourné un JSON valide.\\nSortie brute:\\n{json\_output}")**

    **except Exception as e:**

        **print(f"Erreur lors de la validation ou de l'exécution: {e}")**

        

    **return None**

**\# \--- 5\. Exemple d'Exécution \---**

**if \_\_name\_\_ \== "\_\_main\_\_":**

    

    **\# NOTE: Plus besoin de définir l'ontologie ici**

    **print("=========================================================")**

    **print("🚀 DÉMONSTRATION AGENT-G: ÉTAPE 1 (SANS ONTOLOGIE)")**

    **print("=========================================================\\n")**

    **\# \--- Test 1: Itération 1 (pas de feedback) \---**

    **print("--- Test 1: Itération 1 (t=1) \---")**

    **question\_1 \= "What nanofluid heat transfer papers have been published by John Smith?"**

    **feedback\_1 \= None**

    

    **\# On appelle la fonction** 

    **action\_1 \= run\_agent\_step\_1(question\_1, feedback\_1)**

    

    **if action\_1:**

        **print("\\n✅ Action (a\_t) générée (Itération 1):")**

        **print(action\_1.model\_dump\_json(indent=2))**

        

        **\# Le LLM va deviner les types, par exemple:**

        **\# "entites": \[**

        **\#   {"name": "nanofluid heat transfer", "type": "Sujet de recherche"},**

        **\#   {"name": "John Smith", "type": "Auteur"}**

        **\# \]**

    **print("\\n" \+ "-"\*50 \+ "\\n")**

    **\# \--- Test 2: Itération 2 (avec feedback) \---**

    **print("--- Test 2: Itération 2 (t=2) \---")**

    **question\_2 \= question\_1**

    **feedback\_2 \= "Entity 'nanofluid heat transfer' incorrect. It's textual aspect."**

    

    **\# On appelle à nouveau san**

    **action\_2 \= run\_agent\_step\_1(question\_2, feedback\_2)**

    

    **if action\_2:**

        **print("\\n✅ Action (a\_t) corrigée (Itération 2):")**

        **print(action\_2.model\_dump\_json(indent=2))**

        

        **\# Le LLM devrait corriger son plan en se basant sur le feedback**

        **\# "entites": \[**

        **\#   {"name": "John Smith", "type": "Auteur"}**

        **\# \],**

        **\# "selection\_module": "graph"**

### **Fichier 2 : `requirements.txt`**

### **Pour exécuter ce code :**

**Les étapes sont les mêmes :**

1. **Enregistrez le code ci-dessus en `agent_step_1.py`.**  
2. **Assurez-vous d'avoir `anthropic` et `pydantic` installés (`pip install -r requirements.txt`).**  
3. **Définissez votre clé API (`export ANTHROPIC_API_KEY="votre_cle_api_ici"`).**  
4. **Exécutez le script : `python agent_step_1.py`.**

   **Etape 2: RETRIEVER BANK \- Récupération**

   **Dossier 2 dans le projet nommé RETRIEVAL**

   **Selon le plan généré de l’agent orchestre on va savoir si la question necessite une recherche dans des bases de données textuelles ou dans KG**

* ##### **Si sélection \= 'text' (Text Retrieval Module)**

  **SOUS DOSSIER POUR LE TEXTE CONTIENT 3 SOUS DOSSIERS : STARK \+CRAG  / RANKER**

**RAPPEL:**    
**🔍 Retriever:**

* **STARK:**  
  * 🤖 Modèle: Dense Retrieval avec OpenAI Ada-002  
  * 📥 Input: Question `q`  
  * 🔧 Méthode: Vector Similarity Search (VSS)  
  * 📤 Output: Top-K documents similaires  
* **CRAG:**  
  * 🤖 Modèle: Web Search (pré-fait) \+ BAAI/bge-m3  
  * 📥 Input: Question `q`  
  * 🔧 Méthode: Recherche web \+ embeddings  
  * 📤 Output: Batch de 5 pages web

**📊 Ranker:**

* 🤖 Modèle: Même que retriever (Ada-002 ou bge-m3)  
* 📥 Input: Question \+ documents candidats  
* 🔧 Méthode: Calcul de similarité cosinus dans l'espace d'embeddings  
* 📤 Output: Top-K documents classés `X_t`

**CODE DE RANKER**   
**"""**  
**Implémentation de l'Étape 2A: Ranker pour l'architecture AGENT-G.**

**Ce script prend une question et une liste de documents "candidats"**  
**(récupérés par le Retriever ou la Web Search) et les classe**  
**en fonction de leur pertinence sémantique par rapport à la question.**

**Méthode: Similarité Cosinus entre les embeddings.**  
**Modèles:**  
**\- STARK: OpenAI Ada-002**  
**\- CRAG: BAAI/bge-m3**  
**"""**

**import os**  
**import numpy as np**  
**from typing import List, Dict, Tuple**

**\# \--- Dépendances \---**  
**\# Assurez-vous d'installer les bibliothèques nécessaires:**  
**\# pip install \-r requirements.txt**  
**\# (voir le fichier requirements.txt à la fin)**

**try:**  
    **from openai import OpenAI**  
    **openai\_client \= OpenAI(api\_key=os.environ.get("OPENAI\_API\_KEY"))**  
**except ImportError:**  
    **print("Bibliothèque 'openai' non installée. Le mode STARK ('ada') ne fonctionnera pas.")**  
    **openai\_client \= None**  
**except Exception: \# (par ex. si OPENAI\_API\_KEY n'est pas définie)**  
    **print("OPENAI\_API\_KEY non définie. Le mode STARK ('ada') ne fonctionnera pas.")**  
    **openai\_client \= None**

**try:**  
    **from sentence\_transformers import SentenceTransformer**  
    **\# Initialisation du modèle BGE.**  
    **\# Il sera téléchargé au premier lancement.**  
    **bge\_model \= SentenceTransformer('BAAI/bge-m3')**  
    **print("Modèle BAAI/bge-m3 chargé.")**  
**except ImportError:**  
    **print("Bibliothèque 'sentence-transformers' non installée. Le mode CRAG ('bge') ne fonctionnera pas.")**  
    **bge\_model \= None**

**\# \--- 1\. Fonctions d'Embedding \---**

**def get\_embedding\_stark(text: str) \-\> np.ndarray:**  
    **"""**  
    **Génère un embedding en utilisant OpenAI Ada-002 (pour STARK).**  
    **"""**  
    **if not openai\_client:**  
        **raise Exception("Client OpenAI non initialisé. Vérifiez l'installation et la clé API.")**  
      
    **response \= openai\_client.embeddings.create(**  
        **input=\[text.replace("\\n", " ")\],**  
        **model="text-embedding-ada-002"**  
    **)**  
    **return np.array(response.data\[0\].embedding)**

**def get\_embedding\_crag(texts: List\[str\]) \-\> np.ndarray:**  
    **"""**  
    **Génère des embeddings en utilisant BAAI/bge-m3 (pour CRAG).**  
    **Prend une liste de textes pour un traitement par batch efficace.**  
    **"""**  
    **if not bge\_model:**  
        **raise Exception("Modèle SentenceTransformer (bge-m3) non initialisé.")**  
      
    **\# Pour bge-m3, il est recommandé d'ajouter une instruction**  
    **\# pour les requêtes de "retrieval".**  
    **\# Note : Votre document dit d'utiliser le "Même que retriever",**  
    **\# donc nous utilisons le modèle de base.**  
      
    **\# Le modèle peut encoder plusieurs documents en une seule fois.**  
    **embeddings \= bge\_model.encode(texts, normalize\_embeddings=True)**  
    **return np.array(embeddings)**

**\# \--- 2\. Fonction de Similarité \---**

**def cosine\_similarity(vec1: np.ndarray, vec2: np.ndarray) \-\> float:**  
    **"""**  
    **Calcule la similarité cosinus entre deux vecteurs numpy.**  
    **"""**  
    **\# np.dot(vec1, vec2) calcule le produit scalaire**  
    **\# np.linalg.norm(vec) calcule la magnitude (norme L2)**  
      
    **\# Si les embeddings sont déjà normalisés (comme bge-m3 le fait),**  
    **\# un simple produit scalaire suffit.**  
    **if np.isclose(np.linalg.norm(vec1), 1.0) and np.isclose(np.linalg.norm(vec2), 1.0):**  
        **return np.dot(vec1, vec2)**  
      
    **\# Calcul complet si non normalisé (comme Ada-002)**  
    **sim \= np.dot(vec1, vec2) / (np.linalg.norm(vec1) \* np.linalg.norm(vec2))**  
    **return sim**

**\# \--- 3\. Logique du Ranker \---**

**def run\_ranker(**  
    **question: str,**  
    **documents: List\[str\],**  
    **model\_type: str,**  
    **top\_k: int \= 3**  
**) \-\> List\[Tuple\[str, float\]\]:**  
    **"""**  
    **Classe les documents en fonction de leur similarité avec la question.**

    **Args:**  
    **\- question (str): La question de l'utilisateur (Input q).**  
    **\- documents (List\[str\]): La liste des documents candidats.**  
    **\- model\_type (str): 'stark' (pour Ada-002) ou 'crag' (pour bge-m3).**  
    **\- top\_k (int): Le nombre de meilleurs documents à retourner.**

    **Returns:**  
    **\- List\[Tuple\[str, float\]\]: Liste de (document, score) triée par score.**  
    **"""**  
    **print(f"--- Exécution du Ranker (Mode: {model\_type}) \---")**  
      
    **scores \= \[\]**  
      
    **if model\_type \== 'stark':**  
        **if not openai\_client:**  
            **print("Erreur: Mode STARK impossible sans 'openai'.")**  
            **return \[\]**  
          
        **\# 1\. Obtenir l'embedding de la question**  
        **print("Génération de l'embedding (question) avec Ada-002...")**  
        **question\_emb \= get\_embedding\_stark(question)**  
          
        **\# 2\. Obtenir l'embedding de chaque document et calculer le score**  
        **print(f"Calcul des scores pour {len(documents)} documents...")**  
        **for doc in documents:**  
            **doc\_emb \= get\_embedding\_stark(doc)**  
            **score \= cosine\_similarity(question\_emb, doc\_emb)**  
            **scores.append((doc, score))**

    **elif model\_type \== 'crag':**  
        **if not bge\_model:**  
            **print("Erreur: Mode CRAG impossible sans 'sentence-transformers'.")**  
            **return \[\]**  
              
        **\# 1\. Obtenir l'embedding de la question**  
        **print("Génération de l'embedding (question) avec bge-m3...")**  
        **\# bge-m3 peut prendre une liste, mais pour la question c'est 1 seul**  
        **question\_emb \= get\_embedding\_crag(\[question\])\[0\]**   
          
        **\# 2\. Obtenir l'embedding de tous les documents (en 1 batch)**  
        **print(f"Génération des embeddings (documents) avec bge-m3...")**  
        **doc\_embeddings \= get\_embedding\_crag(documents)**  
          
        **\# 3\. Calculer les scores**  
        **print("Calcul des scores...")**  
        **for doc, doc\_emb in zip(documents, doc\_embeddings):**  
            **\# bge-m3 encode avec normalize\_embeddings=True,**  
            **\# donc un simple 'dot' suffit.**  
            **score \= np.dot(question\_emb, doc\_emb)**  
            **scores.append((doc, float(score)))**

    **else:**  
        **raise ValueError("model\_type doit être 'stark' ou 'crag'")**

    **\# 4\. Trier les documents par score (décroissant)**  
    **scores.sort(key=lambda x: x\[1\], reverse=True)**  
      
    **\# 5\. Retourner le Top-K**  
    **return scores\[:top\_k\]**

**\# \--- 4\. Exemple d'Exécution \---**

**if \_\_name\_\_ \== "\_\_main\_\_":**  
      
    **\# Données d'exemple**  
    **QUESTION \= "What are the latest advancements in solid-state batteries?"**  
      
    **\# Documents candidats (ex: 5 pages web récupérées par le Retriever CRAG)**  
    **DOCUMENTS\_CANDIDATS \= \[**  
        **"Solid-state batteries promise higher energy density and improved safety. Recent research focuses on sulfide electrolytes.", \# Pertinent**  
        **"The history of lithium-ion batteries dates back to the 1970s.", \# Moins pertinent**  
        **"A major challenge for solid-state batteries is the dendrite formation at the anode-electrolyte interface.", \# Très pertinent**  
        **"Stock market analysis for battery technology companies in 2024.", \# Non pertinent**  
        **"Researchers at MIT have developed a new ceramic material that could double the lifespan of solid-state batteries." \# Très pertinent**  
    **\]**  
      
    **print("=========================================================")**  
    **print("🚀 DÉMONSTRATION AGENT-G: ÉTAPE 2A \- RANKER")**  
    **print("=========================================================\\n")**

    **\# \--- Test 1: Mode CRAG (bge-m3) \---**  
    **\# (Ne nécessite pas de clé API)**  
    **if bge\_model:**  
        **print("--- Test 1: Mode CRAG (BAAI/bge-m3) \---")**  
        **ranked\_docs\_crag \= run\_ranker(**  
            **QUESTION,**  
            **DOCUMENTS\_CANDIDATS,**  
            **model\_type='crag',**  
            **top\_k=3**  
        **)**  
          
        **print("\\n✅ Documents classés (Top 3\) \- CRAG:")**  
        **for i, (doc, score) in enumerate(ranked\_docs\_crag):**  
            **print(f"  {i+1}. Score: {score:.4f} | Doc: \\"{doc\[:50\]}...\\"")**  
    **else:**  
        **print("--- Test 1: Mode CRAG (BAAI/bge-m3) \--- SKIPPED")**

    **print("\\n" \+ "-"\*50 \+ "\\n")**

    **\# \--- Test 2: Mode STARK (Ada-002) \---**  
    **\# (Nécessite une clé API OpenAI valide)**  
    **if openai\_client:**  
        **print("--- Test 2: Mode STARK (OpenAI Ada-002) \---")**  
        **ranked\_docs\_stark \= run\_ranker(**  
            **QUESTION,**  
            **DOCUMENTS\_CANDIDATS,**  
            **model\_type='stark',**  
            **top\_k=3**  
        **)**  
          
        **print("\\n✅ Documents classés (Top 3\) \- STARK:")**  
        **for i, (doc, score) in enumerate(ranked\_docs\_stark):**  
            **print(f"  {i+1}. Score: {score:.4f} | Doc: \\"{doc\[:50\]}...\\"")**  
    **else:**  
        **print("--- Test 2: Mode STARK (OpenAI Ada-002) \--- SKIPPED")**

### **Fichier 2 : `requirements.txt`**

**numpy**  
**openai**  
**sentence-transformers**  
**transformers**  
**torch**

### **Pour exécuter ce code :**

1. **Enregistrez le premier bloc dans un fichier `ranker_step_2a.py`.**  
2. **Enregistrez le deuxième bloc dans un fichier `requirements.txt`.**

**Installez les dépendances :**  
**Bash**  
**pip install \-r requirements.txt**

3.   
4. **(Pour le mode STARK uniquement) Définissez votre clé API OpenAI :**  
   * **Sur macOS/Linux : `export OPENAI_API_KEY="votre_cle_api_ici"`**  
   * **Sur Windows (CMD) : `set OPENAI_API_KEY="votre_cle_api_ici"`**

**Exécutez le script :**  
**Bash**  
**python ranker\_step\_2a.py**

5. 

**La première exécution (pour le mode CRAG) prendra un moment pour télécharger le modèle `BAAI/bge-m3`. Les exécutions suivantes seront instantanées.**

[image1]: <data:image/png;base64,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UYH4AwAAmACsWrVqkDDA2mO6/v0C8QcAADDOYccPk/WLMRN/L774YnXAAQdU06ZNy1EDWLNmTXX00UdXzz//fI4al1x99dXV4sWLc/Ag7rrrruryyy/PwQA9oftj+vTpA8Lmz59frVixonPuNAofLnPmzKkts2zZsmrJkiU5eNxS6p9IqY1bCvXllClT6s/RoPxNPtR+X/etde167WPVUf0CvZFFANZO6xc9iT/dtJMmTapt7ty5A+JeeeWVWuwpThOSxN9HPvKR6thjjx2QLqO0SqP0wmVkNMEo/J577slRddh222035OLndBEvHvL96KOPDogTN9xwQx3nSfXaa68d1gSrNEorVIYmu7hgO437ctOmTQPi1J+KU92Uv0RTX4l169ZV119/fR2//fbbVzfeeGNOMiSPP/54nVc+9t5770F1hIGon5rGoK5/t2vZRJO4ieX0U/yVwsYzTf1jtmZ7EH9lEH8jI4sArJ3WL0Yk/g466KBBomPGjBn1DT158uSeF7hIk6DRBCPfe+21V/XMM890wp944olq9913r4Vmt8VPwm633XYbJFq9eMj3IYccUr355puduPvuu68WP2rvaCbVocSfbOHChZ3wd955p+5P1ambYGjqq1tuuaUWuVdeeWWOGjaqw/LlyzvnEs7nnntuSAEZj/88VnT9NH67XcsmmsSNwj2e+in+tjW2Zhu3tPjbWvTax4i/kZFFQD9N688RRxwxKHxrmOqh+uTwsbRLL720LldPIHPceLN+MSLxd95559W7fNpdMhJWF110UX1Te2GKux361Pnhhx9e+9hjjz3qfI7zQtYkaCz+JGq0G2d0rLL1iLXbJHjZZZdVO+20U/Wzn/1sQHism3x7Z1G7XBKKaqfa6wVdZcTjRYsWVeeff34tEmXr16+v45TG9RlK/KmMY445ptOfFqpD7RaV+srtyUK2hEVm7JOXXnqpOuywwwa9WLp06VLE3xCo3y+55JJBi6EW7gULFgy4llH452us9BrripO/KP58X8V8WfyV0mSy+FNe1yeK11JdhirH/aDPLIQjroPMPnWc62ER9cADD3TiXHe33cQ65TYK51ebmgRVxPWJ6WO9Fae6qx72HXfimuptmurj66FwjZ0Y5+shUz/H8pxOfSdz2nwdoo94TWP/y0qoj2N7urWphMWfr1MuR/VxeKy3ha7rmMdc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>

[image2]: <data:image/png;base64,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>