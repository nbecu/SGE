# Guide Utilisateur : Jeux Distribués dans SGE

Ce guide explique comment jouer à un jeu distribué dans SGE.

---

## Vue d'ensemble

Un jeu distribué permet à plusieurs joueurs de jouer ensemble, chacun sur son propre ordinateur. Tous les joueurs se connectent à la même session de jeu via Internet.

### Concepts simples

- **Session** : Une partie de jeu. Chaque session a un identifiant unique.
- **Créer une session** : Démarrer une nouvelle partie (vous êtes le créateur).
- **Rejoindre une session** : Participer à une partie existante créée par quelqu'un d'autre.
- **Rôle de joueur** : Le personnage ou le rôle que vous incarnez dans le jeu (par exemple "Player 1", "Player 2", etc.).

---

## Comment jouer

### Étape 1 : Lancer le jeu

1. Lancez le jeu comme d'habitude (double-cliquez sur le fichier du jeu ou exécutez-le depuis votre terminal).
2. Un dialog de connexion s'ouvre automatiquement.

### Étape 2 : Se connecter à une session

Vous avez deux options :

#### Option A : Créer une nouvelle session

1. Sélectionnez **"Create new session"** (créer une nouvelle session).
2. Un identifiant de session est généré automatiquement.
3. Cliquez sur **"Connect"**.
4. Attendez que d'autres joueurs vous rejoignent.


#### Option B : Rejoindre une session existante

1. Sélectionnez **"Join existing session"** (rejoindre une session existante).
2. La liste des sessions disponibles s'affiche automatiquement.
3. Cliquez sur la session que vous voulez rejoindre dans la liste.
4. Cliquez sur **"Connect"**.


### Étape 3 : Attendre que tous les joueurs soient connectés

Une fois connecté, vous verrez :
- **"Connection Status: Connected to broker"** : Vous êtes connecté ✓
- **"Seed: Synchronized ✓"** : Le jeu est synchronisé ✓
- **"Instances: X/Y connected"** : Nombre de joueurs connectés

**Exemples d'affichage** :
- `Instances: 2/4 connected (waiting for 2 more...)` : Il manque encore 2 joueurs
- `Instances: 4/4 connected ✓` : Tous les joueurs sont connectés, le jeu peut démarrer

Le dialog se ferme automatiquement quand tous les joueurs requis sont connectés.

### Étape 4 : Sélectionner votre rôle

Après la connexion, un dialog s'ouvre pour sélectionner votre rôle de joueur.

1. **Choisissez votre rôle** : Cliquez sur le bouton radio du rôle que vous voulez jouer.
2. **Confirmez** : Cliquez sur **"OK"**.
3. **Attendez** : Si d'autres joueurs n'ont pas encore sélectionné leur rôle, vous verrez : "Waiting for other players to select their roles..."
4. **Le jeu démarre** : Le dialog se ferme automatiquement quand tous les joueurs ont sélectionné leur rôle.

**Note** : Si un rôle affiche "Already taken", cela signifie qu'un autre joueur l'a déjà choisi. Sélectionnez un autre rôle disponible.

### Étape 5 : Jouer

Une fois que tous les joueurs ont sélectionné leur rôle, le jeu démarre automatiquement. Jouez normalement !

---

## Comportements et cas particuliers

### Que faire si je ne peux pas me connecter ?

Si vous voyez un message d'erreur lors de la connexion :

1. **Vérifiez que le broker MQTT est en cours d'exécution**
   - Contactez l'administrateur du jeu ou le créateur de la session
   - Le broker MQTT doit être accessible

2. **Vérifiez votre connexion Internet**
   - Assurez-vous que vous êtes connecté à Internet
   - Vérifiez que votre pare-feu n'bloque pas la connexion

3. **Réessayez**
   - Fermez le dialog d'erreur
   - Cliquez à nouveau sur **"Connect"**

### Que faire si la session n'apparaît pas dans la liste ?

1. **Rafraîchir la liste** : Cliquez sur le bouton 🔄 à côté de "Available Sessions"
2. **Attendre quelques secondes** : La découverte de sessions peut prendre quelques secondes
3. **Vérifier que le créateur est connecté** : Le créateur de la session doit être connecté pour que la session apparaisse

### Que faire si mon rôle préféré est déjà pris ?

Sélectionnez un autre rôle disponible. Chaque joueur doit avoir un rôle unique. Si tous les rôles sont pris, attendez qu'un joueur se déconnecte ou créez une nouvelle session.

### Que se passe-t-il si le créateur se déconnecte ?

Si le créateur de la session se déconnecte :
- La session est automatiquement fermée
- Un message s'affiche : "The session creator has disconnected. The session has been closed."
- Vous devez créer une nouvelle session ou rejoindre une autre session

### Que se passe-t-il si un joueur se déconnecte pendant le jeu ?

- Le jeu continue avec les joueurs restants
- Le joueur déconnecté ne peut plus jouer
- Les autres joueurs peuvent continuer à jouer normalement si le rôle que le joueur qui s'est déconnecté avait n'était pas indispensable au bon déroulement du jeu

---

## Conseils pratiques

### Pour créer une session

1. **Créez la session** : Sélectionnez "Create new session" et cliquez sur "Connect"
2. **Attendez les joueurs** : Les autres joueurs peuvent maintenant rejoindre votre session en sélectionnant "Join existing session" et en choisissant votre session dans la liste

### Pour rejoindre une session

1. **Sélectionnez "Join existing session"** : La liste des sessions disponibles s'affiche automatiquement
2. **Choisissez la session** : Cliquez sur la session que vous voulez rejoindre dans la liste
3. **Cliquez sur "Connect"** : Vous rejoignez automatiquement la session

### Pour jouer en groupe

- **Organisez-vous** : Décidez à l'avance qui crée la session et qui rejoint
- **Communiquez** : Utilisez un chat vocal ou texte pour coordonner la connexion
- **Vérifiez les rôles** : Assurez-vous que chaque joueur sélectionne un rôle différent

---

## Messages d'erreur courants

### "Unable to connect to MQTT broker"

**Cause** : Impossible de se connecter au serveur MQTT.

**Solutions** :
- Vérifiez votre connexion Internet
- Contactez l'administrateur pour vérifier que le serveur MQTT est en cours d'exécution
- Réessayez après quelques secondes

### "Connection timed out"

**Cause** : Le serveur ne répond pas.

**Solutions** :
- Vérifiez votre connexion Internet
- Vérifiez que le serveur MQTT est accessible
- Réessayez

### "The broker may be closed or not running"

**Cause** : Le serveur MQTT n'est pas accessible.

**Solutions** :
- Contactez l'administrateur pour vérifier que le serveur est en cours d'exécution
- Vérifiez que vous utilisez la bonne adresse du serveur

### "Session closed"

**Cause** : La session a été fermée (créateur déconnecté).

**Solutions** :
- Créez une nouvelle session
- Rejoignez une autre session existante

---

## Questions fréquentes

### Puis-je jouer seul ?

Non, un jeu distribué nécessite au moins 2 joueurs. Le nombre minimum de joueurs est indiqué dans le dialog de connexion.

### Puis-je changer de rôle après l'avoir sélectionné ?

Non, une fois que vous avez sélectionné votre rôle et que tous les joueurs ont confirmé, vous ne pouvez plus changer. Le jeu démarre avec les rôles assignés.

### Que se passe-t-il si je ferme le jeu pendant une partie ?

- Si vous êtes le créateur : La session est fermée et tous les autres joueurs sont déconnectés
- Si vous n'êtes pas le créateur : Les autres joueurs peuvent continuer à jouer sans vous

### Puis-je rejoindre une session en cours ?

Non, vous ne pouvez rejoindre une session que si elle n'a pas encore démarré. Une fois que tous les joueurs ont sélectionné leur rôle, la session est verrouillée.

### Combien de temps dois-je attendre pour que les autres joueurs se connectent ?

Cela dépend du nombre de joueurs requis :
- Si le jeu nécessite 4 joueurs exactement : Vous devez attendre que 4 joueurs soient connectés
- Si le jeu accepte 2 à 4 joueurs : Le jeu peut démarrer dès que 2 joueurs sont connectés

Le dialog affiche le nombre de joueurs connectés en temps réel.

---

## Résumé rapide

1. **Lancez le jeu** → Dialog de connexion s'ouvre
2. **Créez ou rejoignez une session** → Cliquez sur "Connect"
3. **Attendez les autres joueurs** → Le dialog se ferme automatiquement
4. **Sélectionnez votre rôle** → Cliquez sur "OK"
5. **Jouez !** → Le jeu démarre automatiquement


