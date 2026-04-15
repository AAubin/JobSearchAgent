# JobSearchAgent
Agent pour automatiser la recherche d'emploi.
L'agent à les outils pour:
- rechercher des postes sur plusieurs localisations (par département pour l'instant) sur l'api de France Travail
- proposer des conseils pour optimiser le cv
- créer une lettre de motivation au format word
- proposer des conseils pour préparer un entretien

Pour que les outils fonctionnent tous, il est nécessaire de:
- Copier son cv dans le répertoire du projet au format pdf, sous le nom cv.pdf
- Créer un fichier .env avec les champs suivants:
  - ANTHROPIC_API_KEY (clé API pour le LLM avec des crédits disponibles)
  - FRANCE_TRAVAIL_CLIENT_ID
  - FRANCE_TRAVAIL_CLIENT_SECRET
  
Les infos de l'api France Travail se trouvent en créant une application sur le site francetravail.io (mon espace) et en ajoutant l'api "Offres d'emploiv2" dans les api autorisées.
 
## Usage
```
pip install -r requirements.txt
python src/main.py
```
