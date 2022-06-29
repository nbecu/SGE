import threading

def cube(n=3):
    print(f"Le cube: {n * n * n}")

def carre(n=3):
    print(f"Le carré: {n * n}")

# création de thread
t1 = threading.Thread(target=carre)
t2 = threading.Thread(target=cube)

# démarrer le thread t1
t1.start()
# démarrer le thread t2
t2.start()

# attendre que t1 soit exécuté
t1.join()
# attendre que t2 soit exécuté
t2.join()

# les deux thread sont exécutés
print("C'est fini!")