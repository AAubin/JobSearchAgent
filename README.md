# JobSearchAgent

Agent pour automatiser la recherche d'emploi, basé sur Claude (Anthropic) et LangGraph.

L'agent dispose des outils suivants :
- Rechercher des postes sur plusieurs localisations (par département) via l'API France Travail
- Proposer des conseils pour optimiser le CV
- Rédiger une lettre de motivation personnalisée au format Word
- Proposer des conseils pour préparer un entretien
- Utiliser ces outils pour une offre externe à l'API France Travail (copiée par l'utilisateur)

Pour enrichir les lettres de motivation, l'agent effectue une recherche internet avec Tavily afin de récupérer le site officiel et les articles de presse de l'entreprise, et construit ainsi un profil de l'entreprise.

Les offres proposées et les lettres créées sont stockées dans une base SQLite. Lorsque l'agent rédige une lettre de motivation, il enregistre automatiquement la candidature avec une date de relance et un statut de suivi.

Après chaque session, le nombre de tokens utilisés et le coût estimé sont calculés et stockés en base.

Après chaque recherche d'offre, l'agent demande à l'utilisateur d'indiquer si les offres l'intéressent. Après avoir rédigé une lettre, il vérifie son nombre de mots, la présence du nom de l'entreprise, et demande à l'utilisateur de la noter.

## Modèles utilisés

- **Agent principal** : `claude-sonnet-4-6` — recherche d'offres, conseils CV, préparation entretien
- **Rédaction de lettres** : `claude-opus-4-7` — génération de lettres de motivation

## Interface Streamlit

L'application Streamlit propose 5 pages :
- **Chat** : échange avec l'agent, sélection du CV actif
- **Candidatures** : tableau de suivi des candidatures (statut, relances)
- **Offres** : visualisation et filtrage des offres sauvegardées
- **Profil** : gestion du profil utilisateur
- **Sessions** : historique des sessions, tokens consommés et coûts

## Prérequis

### CVs
Créer un dossier `CVs/` à la racine du projet et y déposer un ou plusieurs CVs au format PDF. Le CV actif se sélectionne depuis la sidebar de la page Chat.

### Variables d'environnement
Créer un fichier `.env` avec les champs suivants :

```
ANTHROPIC_API_KEY=        # Clé API Anthropic (avec crédits disponibles)
FRANCE_TRAVAIL_CLIENT_ID=
FRANCE_TRAVAIL_CLIENT_SECRET=
TAVILY_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=
```

- **France Travail** : créer une application sur [francetravail.io](https://francetravail.io) et ajouter l'API "Offres d'emploi v2"
- **Tavily** : obtenir une clé sur [app.tavily.com](https://app.tavily.com)
- **LangChain** : variables de tracing à créer sur [smith.langchain.com](https://smith.langchain.com)

## Usage

### Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Docker
```bash
docker compose up --build
```
