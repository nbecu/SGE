# Chantier : Enregistrement d’état et récupération de simulation

Document de cadrage pour les items FUTURE_PLAN lignes 47-50 (Simulation Management & Data).

---

## 1. Synthèse des 4 items

| Item | Description FUTURE_PLAN | Statut dans le code |
|------|-------------------------|----------------------|
| **47** | Create automatic recording of simulation state at each round | **Non implémenté** |
| **48** | Create a recovery system for simulation in case it shuts down (could use `updateAtMaj` function) | **Non implémenté** |
| **49** | Add item in SGModel menu bar to record state of the world, and use saved state as initialization for new simulation | **Non implémenté** |
| **50** | Add the possibility to export gameAction logs | **Déjà implémenté** (voir §2) |

---

## 2. Item 50 – Export gameAction logs : déjà en place

L’item **50** est couvert par l’existant :

- **Méthodes modeler** (SGModel) :
  - `exportGameActionLogs(filename=None, format="csv")` → export vers fichier (CSV ou JSON)
  - `enableAutoSaveGameActionLogs(format="csv", save_path=None)` → sauvegarde automatique à la fermeture
- **Menu** : Settings → **Export GameAction Logs** → CSV / JSON
- **Fermeture** : si des gameActions ont été jouées et `autoSaveGameActionLogs` activé, proposition de sauvegarder les logs (ou sauvegarde automatique si `save_path` est fourni)

**Recommandation** : marquer l’item 50 comme complété dans FUTURE_PLAN (et éventuellement le déplacer en “Completed Items” avec une courte note).

---

## 3. Recoupements et cohérence des items 47, 48, 49

### 3.1 Différence “état du monde” vs “logs d’actions”

- **GameAction logs** (item 50) : qui a fait quelle action, quand (round/phase), sur quelle entité → **traces d’actions**, pas état complet du modèle.
- **État du monde (world state)** (items 47, 49, 48) : **snapshot** du modèle à un instant donné : entités (agents, cellules, tuiles), positions, attributs, variables de simulation, round/phase, etc. C’est ce qu’il faut pour “reprendre” ou “initialiser à partir d’un fichier”.

Les items 47, 48 et 49 portent sur ce **même concept** (état du monde), avec des usages différents.

### 3.2 Quatre usages pour un même format “world state”

- **47 (enregistrement automatique à chaque round)**  
  - Enregistre un **snapshot d’état** à chaque fin de round (ou phase).  
  - Peut servir de base pour :
    - **48** : récupération après crash (reprendre au dernier round enregistré),
    - **49** : proposer des “points de reprise” ou des sauvegardes manuelles au même format.

- **48 (système de récupération après arrêt)**  
  - Utilise des **états enregistrés** (produits par 47 et/ou 49) pour :
    - au redémarrage, proposer “reprendre depuis la dernière sauvegarde” (auto ou manuelle),
    - ou “charger un fichier d’état” comme état initial (recoupe 49).

- **49 (menu : enregistrer / charger l’état du monde)**  
  - **Enregistrement** : un item de menu (ex. Settings ou dédié) pour “Enregistrer l’état du monde” → même format de snapshot que 47.  
  - **Chargement** : “Utiliser un état enregistré comme état initial” pour une **nouvelle** simulation → même mécanisme de chargement que pour 48, mais vu comme “fichier d’initialisation” plutôt que “reprise après crash”.

- **Backward / Undo (bouton backward)**  
  - Le **bouton backward** (action `backwardAction`) permet de **revenir d’un pas en arrière** dans l’historique. Chaque “pas” est soit une **game action**, soit un **nextStep** (changement de phase ou de round). Un clic = annuler le dernier de ces événements (ex. dernière game action, ou dernier nextStep pour revenir à la phase précédente après les actions déjà faites).  
  - La **pile** contient une séquence d’états (après chaque game action et après chaque nextStep) ; on ne garde en mémoire que les **N derniers rounds** ; au-delà, rechargement depuis le disque. La granularité est **alignée sur les messages MQTT** (une action ou un nextStep = un message).  
  - Le même **format world state** sert à cette pile et au chargement depuis disque.

- **Replay d’une session enregistrée (nouveau usage)**  
  - Possibilité pour l’utilisateur de **rejouer une partie (session) enregistrée**. En mode **replay**, l’utilisateur peut avancer et reculer d’un step à l’autre et consulter l’état de la simulation sur les interfaces habituelles de SGE (grilles, dashboards, etc.). Les fichiers world state de la session sont lus depuis le disque (répertoire dédié quand l’utilisateur a choisi “enregistrer la partie”).

En résumé : **un seul format de “world state”** peut servir à **cinq** usages : (47) enregistrement auto, (49) enregistrement/chargement manuel, (48) récupération après arrêt, **backward/undo**, et **replay** de session.

### 3.3 Point “updateAtMaj”

Dans le code, **il n’existe pas de fonction ou hook nommé `updateAtMaj`**.

- **“Maj” dans SGE** :
  - `listOfMajs` / `processedMAJ` : liés au **MQTT** (liste de mises à jour à traiter).
  - `maj_coordonnees()` : mise à jour de l’affichage des **coordonnées du curseur** (timer).
- L’idée du plan (“could use updateAtMaj”) peut être interprétée comme : **s’accrocher à un moment précis du cycle** (par ex. après chaque phase/round) pour enregistrer l’état, de la même façon qu’on a déjà un hook dans `SGTimeManager.nextPhase()` (ex. `dataRecorder.calculateStepStats()`).

**Recommandation** : ne pas chercher une fonction `updateAtMaj` existante, mais **définir un point d’appel explicite** pour “enregistrer l’état” (ex. à la fin de `nextPhase()` ou via un callback enregistrable), réutilisable pour l’enregistrement automatique (47) et cohérent avec 48/49.

---

## 4. Décisions techniques et besoins d’usage

Les choix suivants ont été arrêtés pour la solution technique (réponses utilisateur, à respecter lors de l’implémentation).

### 4.1 Activation (activer / désactiver l’enregistrement)

- **Qui décide** : les **deux** doivent être possibles (modeler dans le script, player dans l’interface), **sauf** si le modeler indique dans le script que l’option n’est **pas** proposée au player.
- **Mode distribué** : l’option d’activer/désactiver l’enregistrement est **souvent interdite au player** (décision modeler). L’option doit être **identique pour toutes les instances** (même valeur sur chaque instance).

### 4.2 Fichiers sur disque (recovery)

- **Objectif** : reprise après **arrêt brutal d’une instance** (plantage ou mauvaise manipulation). L’utilisateur relance la simulation et fait un recovery pour retrouver l’état juste avant le plantage.
- **Mode distribué – une seule instance plante** : l’utilisateur de l’instance qui a planté relance, fait le recovery, et doit **reprendre au même état que les autres instances**. Pour cela : si les autres instances n’ont pas planté, **l’instance en recovery demande aux autres instances** (via MQTT) de lui **envoyer le dernier world state** ; sinon, elle charge depuis son propre fichier de recovery local.
- **Conservation** :
  - Garder les **N dernières sessions** (ex. N = 3, **paramétrable**) avec **rotation** : les fichiers les plus anciens sont supprimés.
  - **Exception** : si l’utilisateur souhaite **enregistrer la partie (session)** pour replay ou archivage, la session est sauvegardée sous forme d’**un seul fichier** par session dans `saved_sessions/` (ex. `MyGame_20250211_143022.json.gz`), afin qu’il **ne soit pas nettoyé** par la rotation. Un fichier `.json.gz` contient un **tableau JSON** de tous les snapshots de la session (un élément par événement) — pas de sous-répertoire. L’utilisateur peut déclencher “enregistrer la partie” **à tout moment** ; le modeler peut aussi activer un **enregistrement automatique à la fermeture** du modèle (avec ou sans message de confirmation), sur le même principe que `enableAutoSaveGameActionLogs`.

### 4.3 Replay d’une session enregistrée

- **Usage** : possibilité pour l’utilisateur de faire un **replay** d’une session (partie) enregistrée.
- **Comportement** : en mode **replay**, l’utilisateur peut **avancer et reculer d’un step à l’autre** et consulter l’état de la simulation sur les **interfaces habituelles de SGE** (grilles, dashboards, etc.). Les états sont lus depuis **un fichier .json.gz** par session (tableau de snapshots) dans `saved_sessions/`.

### 4.4 Mémoire et ralentissement – pile d’événements pour le backward

- **Pile = historique linéaire d’“événements”** : chaque entrée correspond à l’état du monde **après un seul pas** : soit une **game action** (action joueur), soit un **changement de phase ou de round** (nextStep). Exemple de séquence : [ chgtPhase, gameaction, gameaction, chgtPhase, chgtRound, gameaction, chgtPhase, gameaction, gameaction, chgtPhase ]. **Un clic sur backward = un pas en arrière** (on restaure l’état précédent dans cette séquence).
- **Comportement** : s’il y a eu des game actions juste avant, le premier clic backward annule la **dernière game action** ; le clic suivant peut annuler une autre game action ou un nextStep (retour à la phase précédente, après les game actions déjà faites dans cette phase). On ne distingue pas forcément “chgtPhase” et “chgtRound” dans l’implémentation de la pile : ce sont des **nextStep**, un seul type d’événement suffit.
- **Mémoire** : on garde dans la pile **uniquement les événements des N derniers rounds** (ex. N = 3, paramétrable). Au-delà de N rounds, les états ne sont plus en mémoire.
- **Disque** : un snapshot **à chaque fin de round** (ou à chaque fin de phase si le modeler n’a pas limité au round) est sauvegardé sur disque. Pour revenir au-delà des N derniers rounds, on recharge depuis le disque (par ex. état au début d’un round donné).
- **Forward (redo)** : autorisé ; une pile “redo” garde les événements annulés par backward. Dès qu’une **nouvelle action** (game action ou nextStep) est faite après un backward, la pile redo est **tronquée** (plus de redo possible pour la branche annulée).

### 4.5 Mode distribué

- **Qui écrit sur disque** : **chaque instance** écrit sur le disque (ainsi, recovery possible quelle que soit l’instance qui plante).
- **Backward (undo)** : **autorisé** en mode distribué ; **synchronisé via MQTT** (diffusion de la demande de backward pour que toutes les instances reviennent au même état).

### 4.6 Granularité : backward = un pas = un événement (aligné MQTT)

- **Enregistrement automatique (disque)** : points de sauvegarde à **chaque fin de phase** (sauf si le modeler demande uniquement à chaque round).
- **Granularité du backward** : **un clic backward = un pas en arrière** dans la pile d’événements. Chaque “pas” est soit une **game action**, soit un **nextStep** (changement de phase ou de round). C’est la **même granularité que les messages MQTT** : on informe les autres instances quand un utilisateur fait une game action ou un nextStep ; donc la pile et la synchro distribué sont alignées (un backward = “annuler le dernier message”).
- **Phases automatiques** : dans certaines simulations, des changements de phase peuvent être automatiques (transparents pour l’utilisateur). D’un point de vue use-case, les utilisateurs n’ont pas besoin de faire un backward vers un état intermédiaire qui était transparent pour eux ; on peut néanmoins garder ces étapes dans la pile pour cohérence (un backward peut alors “défaire” un nextStep automatique si l’utilisateur clique plusieurs fois).

---

## 5. Existant utile dans SGE

### 5.1 Données déjà enregistrées par round/phase

- **SGDataRecorder** (utilisé dans `SGTimeManager.nextPhase()` via `calculateStepStats()`) :
  - enregistre des **statistiques** par step (round/phase) : entités par type, joueurs, gameActions ;
  - pas un snapshot complet du monde (pas positions, pas tous les attributs de chaque entité).
- **SGEntity.getObjectIdentiferForExport()** et **serialize_any_object** (SGExtensions) :
  - déjà utilisés pour les exports (ex. gameAction logs) ;
  - à réutiliser pour identifier les entités dans un snapshot (et pour sérialiser les références).

### 5.2 Structure du menu (SGModel)

- Menu **Settings** : Entity Tooltips, Enhanced Grid Layout, Themes, **Export GameAction Logs**, Cursor Position.
- **Barre de menu** : le bouton **backward** existe déjà (QAction “&backward”, connecté à `backwardAction`) ; l’implémentation de `backwardAction` (et éventuellement `forwardAction` pour redo) pourra s’appuyer sur la restauration d’un snapshot world state.
- Pour l’item **49** : ajouter par exemple un sous-menu du type **“World state”** ou **“Simulation state”** avec :
  - “Save current state…” (enregistrement manuel),
  - “Load state as initial state…” (chargement pour nouvelle simulation),
  - et éventuellement “Auto-save state at each round” (activation/désactivation du comportement de l’item 47).

### 5.3 TimeManager

- `timeManager.currentRoundNumber`, `timeManager.currentPhaseNumber` : à inclure dans tout snapshot d’état.
- `nextPhase()` : point naturel pour déclencher l’enregistrement automatique (item 47) si l’option est activée.

---

## 6. Proposition d’objectifs clarifiés pour le chantier

### 6.1 À considérer comme hors scope pour ce chantier

- **Item 50** : déjà fait ; à refléter dans FUTURE_PLAN (complété).

### 6.2 Objectifs à couvrir (items 47, 48, 49 + backward + replay)

1. **Format “world state” unique**  
   Définir un format de snapshot (ex. JSON) contenant au minimum :
   - round / phase courants ;
   - pour chaque type d’entité (agents, cellules, tuiles) : type, id, position (cell ou coords), attributs (dictAttributes), et tout ce qui est nécessaire pour recréer l’état ;
   - variables de simulation (nom, valeur) ;
   - éventuellement joueurs et phase courante, etc.  
   Ce format servira à l’enregistrement automatique (47), manuel (49), à la récupération (48), au **backward/undo** (restauration en mémoire) et au **replay**. Les **IDs d’entités** doivent être inclus et **stables** à la restauration (mêmes IDs qu’au moment de la sauvegarde).

2. **Enregistrement**  
   - **Manuel** (49) : item(s) dans le menu SGModel pour “Enregistrer l’état du monde” (choix du fichier).  
   - **Automatique** (47) : option (modeler ou menu) pour enregistrer un snapshot à chaque **fin de phase** (sauf si modeler demande uniquement à chaque round), avec répertoire paramétrable, rotation des N dernières sessions (§4.2), et déplacement vers répertoire “session enregistrée” si l’utilisateur choisit d’archiver la partie.

3. **Chargement**  
   - **Comme état initial d’une nouvelle simulation** (49) : menu “Charger un état enregistré comme état initial” (ou équivalent) → chargement du snapshot puis démarrage du jeu à ce round/phase avec ces entités et variables.  
   - **Récupération après arrêt** (48) : au lancement, si un “dernier état automatique” existe (ou un fichier de recovery), proposer “Reprendre la simulation depuis la dernière sauvegarde”. En **mode distribué**, si les autres instances sont encore en cours, l’instance en recovery **demande via MQTT le dernier world state** aux autres instances ; sinon chargement depuis le fichier local.

4. **Intégration dans le cycle de simulation**  
   - Hook “enregistrer l’état maintenant” appelé :
     - à la **fin de chaque phase** (ou à la fin de chaque round si le modeler l’a demandé) pour l’enregistrement auto disque (47) et pour pousser un **nextStep** dans la pile backward,
     - **après chaque game action** et **après chaque nextStep** pour pousser le nouvel état en tête de pile (ainsi un backward = dépiler et restaurer l’état précédent),
     - depuis le menu pour la sauvegarde manuelle (49).  
   La pile backward reçoit donc un nouvel état à chaque game action et à chaque nextStep (changement de phase/round). On ne distingue pas obligatoirement phase vs round dans la pile (un seul type “nextStep”).  
   Ne pas s’appuyer sur une hypothétique fonction `updateAtMaj` ; documenter les points d’appel (après game action, après nextPhase/nextRound).

5. **Bouton backward / Undo**  
   - **Un clic backward = un pas en arrière** dans la pile d’événements : on restaure l’état **juste avant** le dernier événement (dernière game action ou dernier nextStep). Si des game actions viennent d’être faites, le premier clic annule la **dernière game action** ; les clics suivants annulent soit une game action, soit un nextStep (retour à la phase précédente, après les game actions déjà réalisées dans cette phase).
   - **Pile** : séquence d’états [ …, état_après_event_k, état_après_event_{k-1}, … ] où chaque “event” = une game action ou un nextStep. On ne garde en mémoire que les **événements des N derniers rounds** (ex. N = 3) ; au-delà, on recharge depuis le **disque** (snapshots à chaque round ou phase).
   - **Mode distribué** : backward **synchronisé via MQTT** — la granularité est la même que les messages MQTT (une game action ou un nextStep = un message), donc “backward” = diffusion “annuler le dernier événement”, toutes les instances reviennent au même état.
   - **Forward (redo)** : autorisé ; pile “redo” tronquée dès qu’une nouvelle action (game action ou nextStep) est faite après un backward.

6. **Replay d’une session enregistrée**  
   - Mode **replay** : charger une session dont les world states ont été déplacés dans un répertoire “session enregistrée” ; l’utilisateur avance/recule step par step et consulte l’état sur les interfaces SGE habituelles.

7. **Activation / désactivation**  
   - Proposer l’option au **modeler** (script) et au **player** (menu/UI), sauf si le modeler interdit l’option au player (souvent le cas en distribué). En mode distribué, même réglage pour toutes les instances.

### 6.3 Ordre de travail suggéré

1. Spécifier et implémenter le **format world state** + sérialisation/désérialisation (lecture/écriture fichier).
2. Implémenter **enregistrement manuel** + item de menu “Save state” (49).
3. Implémenter **chargement comme état initial** + item de menu “Load state” (49).
4. Ajouter **enregistrement automatique à chaque round** (47) (option + appel dans le cycle).
5. Ajouter **récovery au démarrage** (48) (détection du dernier état / fichier de recovery + proposition “Reprendre”).
6. Implémenter le **backward/undo** : pile d’événements (état sauvegardé après chaque game action et après chaque nextStep), limitée aux N derniers rounds en mémoire ; un clic backward = un pas en arrière (annuler dernière action ou dernier nextStep) ; au-delà de N rounds, rechargement depuis le disque ; en distribué, synchronisation MQTT (même granularité que les messages).
7. Implémenter le **replay** : mode lecture d’une session enregistrée (avancer/reculer step par step, interfaces SGE).
8. **Mode distribué** : écriture disque sur chaque instance ; recovery avec demande du dernier world state via MQTT si les autres instances sont encore actives ; backward diffusé via MQTT.

---

## 7. Fichiers principaux concernés

- **SGModel.py** : menu (création des items pour 49), options d’auto-save (47), éventuelle détection recovery (48), **backwardAction** (connexion du bouton backward à la restauration d’état), délégation vers un module “state snapshot”.
- **Exemple / test** : `examples/syntax_examples/ex_stepback_and_recovery.py` — copie de `aGameExample` avec une **modelPhase** ajoutée pour couvrir tous les cas (play phases + model phase, game actions + nextStep). Sert à tester l’implémentation et à exemplifier la fonctionnalité.
- **SGTimeManager.py** : appel du hook “save state” à la fin du round (47).
- **SGEntity, SGAgent, SGCell, SGTile, SGEntityType** : fourniture des données à sérialiser (attributs, position, type) et application des données chargées.
- **SGExtensions.py** : `serialize_any_object` / identifiants d’export à réutiliser ; éventuelles helpers de sérialisation.
- Nouveau module dédié (recommandé) : ex. **SGStateSnapshot** ou **state_recording** dans `mainClasses/`, pour format, lecture/écriture, rotation (N sessions), et chargement dans le modèle.
- **MQTT / distribué** : extension du protocole ou des topics pour demander/émettre le dernier world state (recovery) et pour diffuser une action backward (undo synchronisé).

---

## 8. Éléments à préciser ou à trancher

Les points suivants peuvent être spécifiés plus tard (au moment de l’implémentation) ou décidés dès maintenant, selon les priorités.

### 8.1 Format et contenu du snapshot — proposition

Proposition d’un format **fiable**, **rapide** et **adapté aux besoins** (recovery, backward, replay, distribué).

#### Choix de format de données

| Option | Avantages | Inconvénients |
|--------|-----------|---------------|
| **JSON** | Lisible, débogable, interopérable, pas de dépendance binaire, `json` stdlib Python (C) | Plus volumineux et un peu plus lent que binaire |
| **MessagePack** | Binaire, compact, rapide, API proche de JSON | Dépendance externe, moins lisible en debug |
| **Pickle** | Très rapide en Python | Non portable (version Python, classes), risque à la relecture après mise à jour SGE → **à éviter** pour persistance |

**Recommandation** : **JSON** comme format principal pour les **fichiers sur disque** (fiabilité, relecture après évolution du code, debug). Pour la **pile en mémoire** (backward/redo), garder des **objets Python** (snapshot déjà désérialisés) pour éviter des aller-retour JSON à chaque backward/forward ; l’écriture disque (recovery, session enregistrée) se fait en JSON.

**Compression** : **gzip** (`.json.gz`) recommandée pour les fichiers sur disque — forte réduction de taille (états répétitifs), coût CPU modéré. Rendre la compression **optionnelle** pour le recovery si besoin de vitesse ; pour les **saved_sessions**, utiliser **.json.gz** : un fichier par session contenant un **tableau JSON** `[ snapshot1, snapshot2, ... ]` (un snapshot par événement). Un fichier .json.gz ne contient qu’un seul flux = un seul document JSON ; ce document peut être un tableau de N snapshots, donc **pas besoin de sous-répertoire** dans `saved_sessions/` — une session = un fichier.

#### Structure proposée du fichier snapshot (JSON)

```json
{
  "format_version": 1,
  "model_name": "MyGame",
  "timestamp": "2025-02-11T14:30:22",
  "round": 2,
  "phase": 3,
  "phase_name": "Player Turn",
  "entities": {
    "agents": [
      {
        "type_name": "Sheeps",
        "id": 1,
        "cell_id": 42,
        "x": 5,
        "y": 3,
        "dict_attributes": { "health": "good", "hunger": 0 }
      }
    ],
    "cells": [
      {
        "type_name": "Grid1",
        "id": 42,
        "x": 5,
        "y": 3,
        "dict_attributes": { "terrain": "grass" }
      }
    ],
    "tiles": [
      {
        "type_name": "Cards",
        "id": 1,
        "cell_id": 42,
        "face": "front",
        "stack_index": 0,
        "dict_attributes": {}
      }
    ]
  },
  "simulation_variables": [
    { "name": "Score", "value": 100 }
  ],
  "current_player_name": "Player 1"
}
```

- **`format_version`** : entier ; permet d’adapter la lecture aux anciens fichiers lors d’évolutions du schéma.
- **Références** : agent/tile sur cellule via **`cell_id`** (ID stable de la cellule) ; cellule via **`x`, `y`** + `type_name` (grille connue par le modèle). Les **`id`** sont **stables** (inclus et réattribués au chargement).
- **`dict_attributes`** : uniquement des valeurs **sérialisables** (types JSON : str, int, float, bool, list, dict). Les types non sérialisables (Qt, lambdas) sont **exclus** ou **convertis** (ex. `QColor` → `"#rrggbb"`) avant écriture ; à documenter dans le code (allowlist ou convertisseurs par type).

#### Fiabilité

- **Version** : `format_version` en tête ; à la lecture, branchement selon la version pour rester compatible avec d’anciens snapshots.
- **Validation** : à l’écriture, vérifier que toutes les entités nécessaires et les champs obligatoires sont présents ; à la lecture, vérifier la présence de `format_version` et des clés attendues, avec message d’erreur explicite si fichier invalide ou inconnu.
- **Écriture atomique** : écrire dans un fichier temporaire puis **renommer** vers le nom final (éviter un fichier coupé en cas de crash pendant l’écriture).

#### Rapidité

- **Disque** : JSON + gzip optionnel ; écriture **asynchrone** (file d’écriture en arrière-plan) pour ne pas bloquer la simulation (recommandé pour enregistrement à chaque événement en session “enregistrée”).
- **Mémoire (pile backward)** : pas de sérialisation JSON à chaque backward/forward ; garder les **snapshots déjà désérialisés** (structures Python, ou copies légères du modèle) pour les N derniers rounds.
- **Chargement** : lecture JSON (et décompression si gzip) une seule fois au recovery/replay ; désérialisation ciblée (reconstruction des entités avec IDs stables).

#### Résumé des choix proposés

| Besoin | Proposition |
|--------|-------------|
| Format fichier | JSON |
| Version | `format_version` entier en tête |
| Compression | gzip (`.json.gz`) optionnelle pour disque |
| Références | `cell_id`, `id` stables, `x`/`y` pour cellules |
| Types non sérialisables | Exclus ou convertis (ex. couleur → hex) ; pas de lambdas dans le snapshot |
| Fiabilité écriture | Fichier temporaire + renommage atomique |
| Rapidité | Pile en mémoire = objets Python ; écriture disque optionnellement asynchrone |

À valider ou ajuster (ex. adoption de MessagePack en plus pour certains usages, ou schéma exact des convertisseurs Qt).

**Note migration PyQt6** : SGE pourrait migrer vers **PyQt6** dans les mois à venir (voir FUTURE_PLAN). Pour le snapshot, éviter de figer des détails d’implémentation propres à PyQt5 : les convertisseurs pour types Qt (couleurs, etc.) doivent être écrits de façon à rester valables ou facilement adaptables sous PyQt6 (même schéma de sérialisation, ex. `QColor` → hex ; imports ou helpers à isoler pour limiter les changements lors de la migration).

### 8.2 Forward (redo) — décidé

- **Redo autorisé** : le bouton **forward** permet de **redo** (rejouer les événements annulés). Garder une pile “redo” contenant les états/événements annulés par backward ; cette pile redo est **tronquée** dès qu’une nouvelle action (game action ou nextStep) est faite après un backward.

### 8.3 Comportement après backward puis nouvelle action — décidé

- **Oui** : après un backward, si l’utilisateur fait une **nouvelle game action** (ou nextStep), la branche “annulée” est perdue — **plus de redo possible** au-delà de ce point (la pile redo est vidée).

### 8.4 Replay – détails — décidé

- **Granularité** : en replay, on veut **voir chaque action** — même granularité que la pile (un pas = un événement : game action ou nextStep). Les états replay sont la **même séquence** ; on lit le **tableau de snapshots** dans le fichier de la session (un élément par événement).
- **Convention de noms** :
  - **Recovery** : un fichier par snapshot (rotation N sessions), ex. `nomModele_dateHeure_Round_Phase_n°Action.json` ou `.json.gz`.
  - **Saved sessions** : **un seul fichier par session** dans `saved_sessions/`, sans sous-répertoire : `nomModele_dateHeureDeLancement.json.gz`. Le fichier contient un **tableau JSON** `[ snapshot1, snapshot2, ... ]` (un snapshot par événement). Le format **.json.gz** est particulièrement adapté ici (une session = beaucoup d’états, compression efficace).
- **Interface** : **même fenêtre SGE** en mode lecture seule (pas de fenêtre dédiée replay). Désactivation des actions joueur (pas de game action, pas de nextStep), seuls les boutons avancer/reculer permettent de naviguer dans la séquence.

### 8.5 “Enregistrer la partie” (session) — décidé

- **Quand** : l’utilisateur peut déclencher “enregistrer la partie” depuis le menu **à tout moment**. De plus, le **modeler** peut spécifier que l’enregistrement se fasse **automatiquement à la fermeture du modèle** (avec ou sans message de confirmation), sur le même principe que l’enregistrement automatique des game action logs (`enableAutoSaveGameActionLogs`).
- **Contenu** : la session en cours est enregistrée sous forme d’**un seul fichier .json.gz** dans `saved_sessions/` (ex. `saved_sessions/MyGame_20250211_143022.json.gz`), **sans sous-répertoire**. Le fichier contient un **tableau JSON** de tous les snapshots de la session (un élément par événement : game action ou nextStep), ce qui permet le replay pas à pas. Un fichier `.json.gz` ne contient qu’un seul flux compressé, donc un seul “document” JSON — ici ce document est un **tableau** `[ state1, state2, ... ]`. Le format .json.gz est bien adapté aux saved_sessions (compression d’une longue séquence). Nettoyage des fichiers dans `saved_sessions/` : manuel uniquement (pas de rotation auto).

### 8.6 Recovery – cas particuliers — décidé

- **Plusieurs instances plantent** (ex. coupure courant) : chaque instance qui redémarre charge depuis son **fichier local** (dernier état écrit) ; pas de “dernier état global” partagé.
- **Qui répond à la demande MQTT “donne-moi ton dernier state”** : **aucune hiérarchie** entre les instances une fois le jeu démarré (le créateur de la session distribué n’a un rôle que pour le lancement). **N’importe quelle instance** encore en cours peut répondre à la demande de state (première réponse reçue suffit, les états étant identiques).

### 8.7 Performance et limites

- **Écriture disque** : synchrone (bloquant) ou asynchrone (file d’écriture en arrière-plan) pour ne pas ralentir la simulation.
- **Taille cible d’un snapshot** : objectif (ex. < X Mo par état) et stratégie si dépassement (compression, réduction optionnelle des données).
- **Backward désactivé** : quand désactiver le bouton backward ? (pile vide, enregistrement désactivé, phase d’initialisation, mode replay en lecture seule, etc.)

### 8.8 Model actions et état restauré

- Lors d’un **restore** (recovery ou backward), les **model actions** (exécutées à chaque phase) : faut-il les **re-exécuter** à partir de l’état restauré (round/phase) au prochain nextStep, ou considérer que l’état snapshot inclut déjà “tout ce qui a été fait” et ne pas rejouer les model actions ? En général, le snapshot décrit l’état du monde (entités, variables) ; au prochain nextStep, les model actions de la phase courante ont déjà été exécutées pour cet état. À clarifier selon la sémantique choisie (snapshot = avant ou après exécution des model actions de la phase).

### 8.9 Identifiants et stabilité — décidé

- **IDs d’entités** : **oui, les IDs doivent être stables**. À la restauration, les entités sont recréées avec les **mêmes IDs** qu’au moment de la sauvegarde, pour que les références (logs, indicateurs) restent cohérentes. Le format snapshot doit inclure les IDs et le chargement doit les réattribuer.

### 8.10 History (SGEntity, SGPlayer) et DataRecorder — décidé

- **Deux types d'histoire** :
  - **`history["value"]`** (SGEntity, SGPlayer) : pour chaque attribut, liste de `[round, phase, valeur]` ; rempli par `saveValueInHistory` à chaque `setValue`. Utilisé par **SGDataRecorder** via `getListOfStepsData()` / `getListOfUntagedStepsData()` pour les **graphiques d'évolution des attributs** (entités et joueurs).
  - **`history["performed"]`** (game actions, SGAbstractAction) : liste des actions effectuées (chaque entrée contient round, phase, entité cible, etc.). Utilisé par **SGDataRecorder.getStepsData_ofGameActions()** → **getStatsOfGameActions()** pour les **graphiques d'utilisation des game actions** par (round, phase).
- **Snapshot** :
  - **`history["value"]`** : **non inclus** dans le snapshot (volumineux). À la **restauration** (backward ou load), on **trim** l’historique en mémoire : pour chaque entité et chaque joueur, on ne garde dans `history["value"]` que les entrées dont (round, phase) ≤ (round/phase restauré). Pour la **pile backward/redo en mémoire**, les snapshots doivent inclure `history["value"]` (paramètre `include_history_value=True` dans `build_snapshot_from_model`) afin qu'au **redo** l'historique soit entièrement restauré et que les graphiques ne plantent pas. Ainsi les interfaces de graphiques ne voient jamais de steps « dans le futur » par rapport à la simulation en cours et ne plantent pas.
  - **`history["performed"]`** : **inclus** sous forme simplifiée : pour chaque game action, on enregistre `history_performed` = liste de `[round, phase]` (une entrée par exécution). À la restauration, on recrée `action.history["performed"]` avec des entrées minimales pour que **getStatsOfGameActions()** conserve les bons comptages par step → les graphiques d'utilisation des game actions restent corrects après load/recovery.

---

Ces éléments peuvent rester “ouverts” jusqu’à la phase de conception détaillée ou au début de l’implémentation ; les décisions prises peuvent alors être ajoutées dans ce document.

---

## 9. Résumé pour FUTURE_PLAN

- **Item 50** : à marquer complété (export gameAction logs déjà en place).
- **Items 47, 48, 49 + backward + replay** : à traiter ensemble comme un **chantier unique** “enregistrement d’état et récupération”, avec un **format world state commun** servant à :
  - 49 : menu enregistrer / charger état (manuel),
  - 47 : enregistrement automatique (à chaque phase, ou à chaque round si demandé par le modeler), rotation N sessions, option “enregistrer la partie” (déplacement vers répertoire protégé),
  - 48 : récupération après arrêt (chaque instance écrit sur disque ; en distribué, recovery possible via demande du dernier state aux autres instances via MQTT),
  - **backward/undo** : pile mémoire N derniers rounds + disque pour les rounds plus anciens, synchronisé via MQTT en distribué,
  - **replay** : lecture d’une session enregistrée (avancer/reculer step par step sur les interfaces SGE).

Ce document peut être conservé dans `docs/` et mis à jour au fur et à mesure du chantier (décisions de format, emplacement du hook, nom des entrées de menu).
