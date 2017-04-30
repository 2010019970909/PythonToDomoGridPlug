import re
import os
import time
import datetime
import requests
from threading import Thread
    
#Liste de thread
list_threads=list()

#Objet prise
class prise:
    #Constructeur de l'objet prise
    def __init__(self, n, u):
        self.nom = n
        self.url = u
    
    #Assignation de l'état de la prise
    def setState(self,e):
        if(e==0 or e=='0'):
            requests.get('http://'+self.url+'.local/0')
            #print('off')
        elif(e==1 or e=='1'):
            requests.get('http://'+self.url+'.local/1')
            #print('on')
        elif(e==2 or e=='2'):
            requests.get('http://'+self.url+'.local/b')
            #print('bascule')

    #Obtention de l'état de la prise
    def getUrl(self):
        return self.url
    
    #Obtention de l'alias de la prise
    def getNom(self):
        return self.nom
    
    #Obtention de la puissance instantanée de la prise
    def getPuissance(self):
        r = requests.get('http://'+self.url+'.local/p')
        return r.text
    
    #Otention de la valeur de la quantité d'énergie consommée
    def getEnergie(self):
        r = requests.get('http://'+self.url+'.local/e')
        return r.text
    
    #Otention de la valeur de l'état de la prise
    def getState(self):
        r = requests.get('http://'+self.url+'.local/')
        return r.text
    
    #Obtention de la valeur de l'atténuation du signal WiFi reçu par la prise
    def getRssi(self):
        r = requests.get('http://'+self.url+'.local/')
        return r.text
    
#Objet tâche          
class tache:
    #Constructeur de l'objet classe          
    def __init__(self, n, e, d):
        self.nom = n
        self.etat = e
        self.date = d
    
    #Otention de l'alias de la classe
    def getNom(self):
        return self.nom
    
    #Obtention de l'état à assigner à la prise
    def getEtat(self):
        return self.etat
    
    #Obtention de la date et de l'heure à laquelle la tâche doit avoir lieu
    def getDate(self):
        return self.date

#Thread action sur la prise
class action(Thread):
    #Constructeur de la classe action
    def __init__(self, p, e):
        Thread.__init__(self)
        self.prise = p
        self.element = e
    
    #Programme lancé dans le thread
    def run(self):
        #On essaie de lancer la tâche
        try:
            self.prise.setState(self.element.getEtat())
            #On enregistre le succès de l'exécusion de la tâche.
            log('Succès, tâche \''+str(self.prise.getNom())+'\', mise à l\'état '+str(self.element.getEtat()))
            
        #En cas d'échec
        except:
            #On détermine quelle tâche devait être lancée
            if int(self.element.getEtat())==0:
                e = '0'
                
            elif int(self.element.getEtat())==1:
                e = '1'

            elif int(self.element.getEtat())==2:
                e = 'b'
            else:
                e = '[INCONNU]'
                
            erreur = 'Erreur sur la prise ' + '\'' + self.prise.getNom() + '\', à l\'adresse : \'http://'+self.prise.getUrl()+'.local/'+e+'\''
            print(erreur)
            #On log l'erreur
            log(erreur)
            
#Log des erreurs et succès des différents évènements du programme.
def log(message):
    log = open("erreurs.log", "a")
    erreur = str(datetime.datetime.now()) + ' ' + message +'\n'
    log.write(message)
    log.close()

try:
    #On indique l'heure et la date du démarrage.
    S='Programme démarré, le '+str(datetime.datetime.now())
    print('Programme démarré, le '+str(datetime.datetime.now()))
    log(S)

    while 1:
        #Lecture du fichier contenant les données des prises (nom et adresse)
        with open("Prises.txt", "r") as prises:
            #Import des informations dans une chaîne de caractère
            info_prises = prises.read()
        info_prises = info_prises.replace('\n', ',').replace(' ', ' ').rstrip()
        #Mise en formes des données en fonctions des séparateurs (on crée une liste)
        m = re.split(',', info_prises.lstrip(' ').rstrip(' '))
        
        #On enlève tous les espaces avant et après les paramètres
        i=0
        while i < len(m):
            m[i]=str(m[i]).lstrip(' ').rstrip(' ')
            i+=1

        #On crée une liste pour y stocker des objets de type prise
        list_prises=list()
        for i in range(0,len(m)-1,2):
            #On complète la liste en contruissant les objets à partir de la liste m qui contient tous les paramètres
            list_prises.append(prise(str(m[i]), str(m[i+1])))

        while 1:
                #Lecture du fichier de tâches
                with open("Taches.txt", "r") as taches:
                    info_taches = taches.read()
                info_taches = info_taches.replace('\n', ',').replace(' ', ' ').rstrip() 
                m = re.split(',', info_taches.lstrip(' ').rstrip(' '))
                i=0
                while i < len(m):
                    m[i]=str(m[i]).lstrip(' ').rstrip(' ')
                    i+=1
                    
                list_taches=list()
                for i in range(0,len(m)-1,3):
                    list_taches.append(tache(str(m[i]), str(m[i+1]), datetime.datetime.strptime(str(m[i+2]), '%Y-%m-%d %H:%M:%S.%f')))
                new_task_list=list()
                new_task_list=[]
                
                #On détermine quelles tâches sont à exécuter et on réécrit le document de tâche avec les tâches restantes
                c=0
                for i in range(0,len(list_taches)):
                    if list_taches[i].getDate()<datetime.datetime.now():
                        for j in range(0,len(list_prises)):
                            if list_prises[j].getNom()==list_taches[i].getNom():
                                task=list_taches[i]
                                list_threads.append(action(list_prises[j],list_taches[i]))
                                c=1
                                
                        if c==0:
                            #Ce message apparaît si il n'existe aucun alias de prise correspondant
                            log('Erreur, aucune prise ne peut effectuer la tâche \''+list_taches[i].getNom()+'\'')
                    else:
                        #On créer une liste avec les tâches à garder
                        new_task_list.append(list_taches[i])
                        
                #On vérifie si il est nécessaire de réécrire le fichier de tâche
                if len(new_task_list)<len(list_taches):
                    f_tache = open("Taches.txt", "w")
                    print(datetime.datetime.now())
                    for i in range(0,len(new_task_list)):
                        f_tache.write(new_task_list[i].getNom()+','+new_task_list[i].getEtat()+','+str(new_task_list[i].getDate())+'\n')
                    f_tache.close()
                 
                #On démarre l'accomplissement des tâches (un thread par tâche)
                for k in range(0,len(list_threads)):
                    new_thread=list_threads[k]
                    new_thread.start()
                list_threads=[]
                #time.sleep(1)
    exit(0)

except:
    log('Exception majeure')
    exit(1)
