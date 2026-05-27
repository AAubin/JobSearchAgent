# JobSearchAgent
Agent pour automatiser la recherche d'emploi.
L'agent à les outils pour:
- rechercher des postes sur plusieurs localisations (par département pour l'instant) sur l'api de France Travail
- proposer des conseils pour optimiser le cv
- créer une lettre de motivation au format word
- proposer des conseils pour préparer un entretien
- Utiliser ces outils pour une offre externe à l'api france travail (copiée par l'utilisateur)

Pour enrichir et personnaliser les lettres de motivation, l'agent fait une recherche internet avec Tavily pour récupérer le site officiel et les articles de presses de l'entreprise et ainsi créer un profil de l'entreprise.

Les offres proposées et les lettres crées sont stockés dans des tables d'une database sqlite. 
Si l'agent rédige une lettre de motivation il considère qu'une candidature a été effectuée et l'enregistre dans une table dédiée, avec une date de relance et l'état de la candidature (interface pour le suivi à venir).
Après chaque session, le nombre de tokens utilisés est récupéré et le coût est calculé. Ces informations sont également stockés dans la database

Après chaque recherche d'offre, l'agent demande à l'utilisateur d'indiquer si les offres l'intéressent, et propose de créer une candidature pour l'une de son choix. Après avoir créer une lettre, il vérifie son nombre de mots, si le nom de l'entreprise est bien dedans, et demande à l'utilisateur de la noter.
Toutes ces informations seront exploités par la suite lors de la création d'une IHM (de même que le tableau de suivi)

Pour que les outils fonctionnent tous, il est nécessaire de:
- Copier son cv dans le répertoire du projet au format pdf, sous le nom cv.pdf
- Créer un fichier .env avec les champs suivants:
  - ANTHROPIC_API_KEY (clé API pour le LLM avec des crédits disponibles)
  - FRANCE_TRAVAIL_CLIENT_ID
  - FRANCE_TRAVAIL_CLIENT_SECRET
  - LANGCHAIN_TRACING_V2=true
  - LANGCHAIN_API_KEY
  - LANGCHAIN_PROJECT
  - TAVILY_API_KEY
  
Les infos de l'api France Travail se trouvent en créant une application sur le site francetravail.io (mon espace) et en ajoutant l'api "Offres d'emploiv2" dans les api autorisées. 
Les variables Langchain sont à créer et obtenir sur smith.langchain.com. 
La clé TAVILY est à créer sur app.tavily.com.
 
## Usage
```
pip install -r requirements.txt
python src/main.py
```
