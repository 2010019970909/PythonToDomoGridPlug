import re
import os
import time
import datetime
import requests
from threading import Thread

def p():
    print('debug')
    
#Liste de thread
list_threads=list()

#Objet prise
class prise:
    def __init__(self, n, u):
        self.nom = n
        self.url = u
        
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

    def getUrl(self):
        return self.url

    def getNom(self):
        return self.nom

    def getPuissance(self):
        r = requests.get('http://'+self.url+'.local/p')
        return r.text
    
    def getEnergie(self):
        r = requests.get('http://'+self.url+'.local/e')
        return r.text
    
#Objet tâche          
class tache:
    def __init__(self, n, e, d):
        self.nom = n
        self.etat = e
        self.date = d

    def getNom(self):
        return self.nom

    def getEtat(self):
        return self.etat

    def getDate(self):
        return self.date

#Thread action sur la prise
class action(Thread):
    def __init__(self, p, e):
        Thread.__init__(self)
        self.prise = p
        self.element = e

    def run(self):
        try:
            self.prise.setState(self.element.getEtat())
            log('Succès, tâche \''+str(self.prise.getNom())+'\', mise à l\'état '+str(self.element.getEtat()))

        except:
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
            log(erreur)
            
#Log
def log(erreur):
    log = open("erreurs.log", "a")
    erreur = str(datetime.datetime.now()) + ' ' + erreur +'\n'
    log.write(erreur)
    log.close()

try:
    print('Programme démarré, le '+str(datetime.datetime.now()))

    while 1:
        #Lecture du fichier contenant les données des prises (nom et adresse)
        with open("Prises.txt", "r") as prises:
            info_prises = prises.read()
        info_prises = info_prises.replace('\n', ',').replace(' ', ' ').rstrip()
        m = re.split(',', info_prises.lstrip(' ').rstrip(' '))

        i=0
        while i < len(m):
            m[i]=str(m[i]).lstrip(' ').rstrip(' ')
            i+=1

        list_prises=list()
        for i in range(0,len(m)-1,2):
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
                c=0
                for i in range(0,len(list_taches)):
                    if list_taches[i].getDate()<datetime.datetime.now():
                        for j in range(0,len(list_prises)):
                            if list_prises[j].getNom()==list_taches[i].getNom():
                                task=list_taches[i]
                                list_threads.append(action(list_prises[j],list_taches[i]))
                                c=1
                                
                        if c==0:
                            log('Erreur, aucune prise ne peut effectuer la tâche \''+list_taches[i].getNom()+'\'')
                    else:
                        new_task_list.append(list_taches[i])
                
                if len(new_task_list)<len(list_taches):
                    f_tache = open("Taches.txt", "w")
                    print(datetime.datetime.now())
                    for i in range(0,len(new_task_list)):
                        f_tache.write(new_task_list[i].getNom()+','+new_task_list[i].getEtat()+','+str(new_task_list[i].getDate())+'\n')
                    f_tache.close()
  
                for k in range(0,len(list_threads)):
                    new_thread=list_threads[k]
                    new_thread.start()
                    
                list_threads=[]
                time.sleep(1)
    exit(0)

except:
    exit(1)
