# Odoo + Payzen by OSB

Ce projet contient le setup initial pour:
- un serveur Odoo 15.0
- la base de données postgres associée
- le module OSB Payzen

# Setup

- Récupérez ce dossier
- renommer/copier exemple.env en .env
- remplacer les valeurs de .env
- lancez la commande suivante:

```bash
docker-compose up -d
```

- commentez la commande qui lance first-start.sh dans docker-compose.yml
