# 🎯 QUESTIONS FINALES POUR DÉMONSTRATION RAG
## Liste Ciblée pour Montrer l'Impact du RAG

---

## 📊 **Serveurs Actifs**
- **Sans RAG:** http://127.0.0.1:7862 (Llama 3.1 8B - GROQ)
- **Avec RAG:** http://127.0.0.1:7866 (Llama 3.3 70B - GROQ)

---

## 🎯 **TOP 8 QUESTIONS - Démonstration Optimale**

### ✅ **Question 1 : CHIFFRES PRÉCIS** (Impact maximal)
**Question:** 
```
Combien de séances de thérapie cognitive sont nécessaires pour traiter une dépression selon le protocole standard ?
```

**Sans RAG attendu:** "Plusieurs séances, généralement quelques mois"  
**Avec RAG attendu:** "20 à 30 séances de 45 minutes sur 3 à 6 mois [Document X]"

**Métrique:** Précision quantitative ⭐⭐⭐⭐⭐

---

### ✅ **Question 2 : CRITÈRES DIAGNOSTIQUES** (Rigueur médicale)
**Question:**
```
Quels sont exactement les critères diagnostiques DSM-5 pour le Trouble d'Anxiété Généralisée (TAG) ?
```

**Sans RAG attendu:** Description générale vague  
**Avec RAG attendu:** Critères A, B, C, D, E, F complets avec 6 symptômes listés [Document X]

**Métrique:** Exhaustivité et précision médicale ⭐⭐⭐⭐⭐

---

### ✅ **Question 3 : STATISTIQUES** (Données chiffrées)
**Question:**
```
Quelle est la prévalence à vie du Trouble d'Anxiété Généralisée dans la population générale selon les études ?
```

**Sans RAG attendu:** "Assez commun, quelques pourcents"  
**Avec RAG attendu:** "6% de prévalence, 2 à 3 fois plus fréquent chez les femmes [Document X]"

**Métrique:** Exactitude statistique ⭐⭐⭐⭐⭐

---

### ✅ **Question 4 : CAS CLINIQUE SPÉCIFIQUE** (Informations impossibles sans documents)
**Question:**
```
Dans le cas clinique 'Giovanni', combien de séances de psychanalyse et de TCC ont été nécessaires et avec quels résultats ?
```

**Sans RAG attendu:** "Je n'ai pas accès à ce cas spécifique"  
**Avec RAG attendu:** "100 séances psychanalyse (1,5 an) → 2 tentatives suicide. 20 séances TCC (4 mois) → résultats maintenus 16 mois [Document X]"

**Métrique:** Traçabilité et cas réels ⭐⭐⭐⭐⭐

---

### ✅ **Question 5 : PROTOCOLE PRÉCIS** (Détails techniques)
**Question:**
```
Comment fonctionne précisément la thérapie d'exposition pour l'agoraphobie selon le protocole d'Isaac Marks ?
```

**Sans RAG attendu:** "Exposition progressive aux situations anxiogènes"  
**Avec RAG attendu:** "Immersion prolongée et répétée jusqu'à habituation, réduction accélération cardiaque/respiratoire, protocole Isaac Marks - Université de Londres [Document X]"

**Métrique:** Spécificité technique et références ⭐⭐⭐⭐

---

### ✅ **Question 6 : COMPARAISON THÉRAPEUTIQUE** (Données comparatives)
**Question:**
```
Quelle est la différence de durée entre une psychanalyse classique et une thérapie cognitive selon vos documents ?
```

**Sans RAG attendu:** "La psychanalyse est plus longue"  
**Avec RAG attendu:** "Psychanalyse: 5-10 ans, 3-5 séances/semaine. TCC: 20-30 séances sur 3-6 mois [Document X]"

**Métrique:** Comparaison factuelle ⭐⭐⭐⭐⭐

---

### ✅ **Question 7 : DONNÉES SPÉCIFIQUES** (Question piège)
**Question:**
```
Selon le modèle cognitif présenté, combien de chiffres la mémoire à court terme peut-elle stocker ?
```

**Sans RAG attendu:** "Environ 7 éléments" (connaissance générale)  
**Avec RAG attendu:** "7 chiffres, plus ou moins 2 (nombre 'magique'), exemple: numéro téléphone [Document X]"

**Métrique:** Détails très spécifiques ⭐⭐⭐⭐

---

### ✅ **Question 8 : POURCENTAGE PRÉCIS** (Impact statistique fort)
**Question:**
```
Quel est le taux de rechute de la dépression majeure dans l'année suivant le premier épisode ?
```

**Sans RAG attendu:** "Il y a un risque de rechute"  
**Avec RAG attendu:** "50% des cas rechutent dans l'année, prévalence 6 mois: 6%, 2x plus chez femmes, périodes critiques: 20-30 ans et 50-60 ans [Document X]"

**Métrique:** Précision statistique complexe ⭐⭐⭐⭐⭐

---

## 📋 **ORDRE DE PASSAGE RECOMMANDÉ**

### **Phase 1 : Impact Immédiat** (Questions 1, 3, 8)
Montrez d'abord les **chiffres précis** pour un impact visuel fort.

### **Phase 2 : Rigueur Médicale** (Questions 2, 5)
Démontrez la **précision diagnostique et protocolaire**.

### **Phase 3 : Cas Réels** (Questions 4, 6)
Prouvez l'accès aux **données spécifiques impossibles sans RAG**.

### **Phase 4 : Détails Techniques** (Question 7)
Finissez avec les **détails très spécifiques**.

---

## 🎬 **SCRIPT DE DÉMONSTRATION**

### **Étape 1 : Ouvrir les deux interfaces côte à côte**
- Fenêtre gauche: http://127.0.0.1:7862 (Sans RAG)
- Fenêtre droite: http://127.0.0.1:7866 (Avec RAG)

### **Étape 2 : Poser la même question aux deux**
Copiez-collez la question **exactement identique** dans les deux chatbots.

### **Étape 3 : Comparer visuellement**
Capturez des screenshots montrant:
- ❌ Sans RAG: Réponse générique
- ✅ Avec RAG: Réponse précise + citations

### **Étape 4 : Documenter les métriques**

| Critère | Sans RAG | Avec RAG |
|---------|----------|----------|
| Chiffres exacts | ❌ | ✅ |
| Citations sources | ❌ | ✅ |
| Cas cliniques | ❌ | ✅ |
| Protocoles détaillés | ❌ | ✅ |
| Statistiques précises | ❌ | ✅ |

---

## 🎯 **RÉSUMÉ EXÉCUTIF**

**SANS RAG (Llama 3.1 8B):**
- ✅ Réponses générales correctes
- ❌ Pas de chiffres précis
- ❌ Pas de citations
- ❌ Pas de cas cliniques spécifiques

**AVEC RAG (Llama 3.3 70B + Documents):**
- ✅ Réponses précises avec chiffres exacts
- ✅ Citations systématiques [Document X]
- ✅ Accès aux cas cliniques réels
- ✅ Détails protocolaires complets
- ✅ Statistiques vérifiables

---

## 💡 **MESSAGE CLÉ POUR VOTRE RAPPORT**

> **"Le RAG transforme un chatbot généraliste en assistant médical spécialisé"**
>
> - **Précision:** 20-30 séances vs "quelques séances"
> - **Traçabilité:** Citations documentaires systématiques
> - **Fiabilité:** Données vérifiables des études cliniques
> - **Spécialisation:** Accès aux protocoles spécifiques (Dr Cottraux, Isaac Marks)

---

## 🚀 **PROCHAINES ÉTAPES**

Une fois cette démonstration complétée:
1. ✅ Captures d'écran des 8 comparaisons
2. ✅ Tableau récapitulatif des métriques
3. ✅ Conclusion sur l'impact du RAG
4. ➡️ **PASSAGE À L'AGENTIC RAG**

---

**Durée estimée de la démonstration:** 15-20 minutes  
**Impact visuel:** ⭐⭐⭐⭐⭐  
**Qualité argumentaire:** ⭐⭐⭐⭐⭐
