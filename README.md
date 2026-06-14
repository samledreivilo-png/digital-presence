# 📊 Analyseur de Présence Digitale

Une mini application web locale pour mesurer la visibilité d'une entreprise sur les réseaux sociaux.

---

## 🎯 Ce que ça fait

Tu entres un nom d'entreprise → l'app cherche ses comptes sur Instagram, TikTok, Facebook et LinkedIn → elle te donne un **score sur 100**.

| Réseau    | Points max | Critères                        |
|-----------|------------|---------------------------------|
| Instagram | 40 pts     | Présence + activité + followers |
| TikTok    | 20 pts     | Présence + followers            |
| Facebook  | 20 pts     | Page active                     |
| LinkedIn  | 20 pts     | Page entreprise                 |

---

## 🚀 Installation étape par étape (débutant complet)

### Étape 1 — Vérifie que Python est installé

Ouvre un terminal (ou PowerShell sur Windows) et tape :

```bash
python --version
```

Tu dois voir quelque chose comme `Python 3.10.x`. Si ce n'est pas le cas, télécharge Python sur https://python.org

---

### Étape 2 — Télécharge le projet

Soit tu télécharges le ZIP, soit tu clones avec Git :

```bash
# Avec Git
git clone https://github.com/TON_USER/digital-presence.git
cd digital-presence

# Ou bien tu navigues dans le dossier si tu as le ZIP
cd chemin/vers/digital-presence
```

---

### Étape 3 — Crée un environnement virtuel

Un environnement virtuel = une boîte isolée pour installer les dépendances du projet sans tout mélanger.

```bash
# Créer l'environnement
python -m venv venv

# L'activer (Mac/Linux)
source venv/bin/activate

# L'activer (Windows)
venv\Scripts\activate
```

Tu dois voir `(venv)` apparaître au début de ta ligne de commande. ✅

---

### Étape 4 — Installe les dépendances

```bash
pip install -r requirements.txt
```

---

### Étape 5 — Installe Playwright et son navigateur

Playwright a besoin de télécharger Chromium (le navigateur qui va faire le scraping) :

```bash
playwright install chromium
```

⏳ Cette étape peut prendre 1-2 minutes. C'est normal.

---

### Étape 6 — Lance l'application !

```bash
streamlit run app.py
```

Ton navigateur s'ouvre automatiquement sur `http://localhost:8501` 🎉

---

## 📁 Structure du projet

```
digital-presence/
│
├── app.py              ← Interface web (Streamlit)
├── requirements.txt    ← Liste des librairies Python
├── README.md           ← Ce fichier
│
└── src/
    ├── __init__.py
    └── scraper.py      ← Moteur de scraping (Playwright)
```

---

## 🧠 Comment ça marche ? (explication simple)

1. **Tu entres un nom** → ex: "Nike"
2. **Le scraper construit des URLs** → `instagram.com/nike`, `tiktok.com/@nike`, etc.
3. **Playwright ouvre un vrai navigateur** (invisible) et visite chaque page
4. **Il analyse le contenu** pour détecter si le compte existe + extraire les followers
5. **Le score est calculé** selon les règles de points
6. **Streamlit affiche tout** dans une belle interface

---

## ⚠️ Limitations connues

- **Instagram** bloque souvent les robots → les followers peuvent ne pas apparaître
- **LinkedIn** nécessite un compte pour voir certaines infos
- Les résultats dépendent de la vitesse de ta connexion internet
- Si le nom de l'entreprise a une URL différente (ex: BN pour BoulangeriePaul), le profil peut ne pas être trouvé

---

## 🛠️ Dépannage

**Erreur `ModuleNotFoundError`** → Tu as oublié d'activer le venv ou d'installer les dépendances.

**Erreur `playwright install`** → Relance avec `python -m playwright install chromium`

**L'app ne s'ouvre pas** → Va manuellement sur `http://localhost:8501` dans ton navigateur

**Timeout sur tous les réseaux** → Vérifie ta connexion internet
