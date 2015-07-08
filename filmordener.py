#! /usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# Name: film_ordener.py
# Author:   Hugo Rodde
# Created: 15/01/2012
################################################################################
# Zenity fonctions
# Licence: MIT Licence
# 
# Copyright (c) 2005 Brian Ramos
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation the 
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
# sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
################################################################################

import glob
import urllib2
import os
import sys
import re
from subprocess import Popen, PIPE

__author__="hugo"
__date__ ="$25 mai 2011 19:14:28$"

zen_exec = 'zenity'

def run_zenity(type, *args): 
    """#Lance une commande zenity avec des arguments"""
    return Popen([zen_exec, type] + list(args), stdin=PIPE, stdout=PIPE)

def get_folder(): 
    """#Affiche à user une boite de dialogue pour selectionner un repertoire"""
    args = ['--directory']
    p = run_zenity('--file-selection', *args)

    if p.wait() == 0:
        return p.stdout.read().strip().split('|')[0]

def info(text): 
    """#Affiche une boite de dialogue avec un texte
    text - texte à afficher"""
    run_zenity('--info', '--text=%s' % text).wait()

def question(text):
    """#Affiche une boite de dialogue avec une question
    text - question à afficher"""
    return run_zenity('--question', '--text={0}'.format(text)).wait() == 0



def process(text='', percentage=0, auto_close=False, pulsate=False):
    """Show a progress dialog to the user.

    This will raise a Zenity Progress Dialog.  It returns a callback that 
    accepts two arguments.  The first is a numeric value of the percent 
    complete.  The second is a message about the progress.

    NOTE: This function sends the SIGHUP signal if the user hits the cancel 
          button.  You must connect to this signal if you do not want your 
          application to exit.

    text - The initial message about the progress.
    percentage - The initial percentage to set the progress bar to.
    auto_close - True if the dialog should close automatically if it reaches 
                 100%.
    pulsate - True is the status should pulsate instead of progress."""

    args = []
    if text:
        args.append('--text=%s' % text)
    if percentage:
        args.append('--percentage=%s' % percentage)
    if auto_close:
        args.append('--auto-close=%s' % auto_close)
    if pulsate:
        args.append('--pulsate=%s' % pulsate)

    p = Popen([zen_exec, '--progress'] + args, stdin=PIPE, stdout=PIPE)

    def update(percent, message=''):
        if type(percent) == float:
            percent = int(percent * 100)
        p.stdin.write(str(percent) + '\n')
        if message:
            p.stdin.write('# %s\n' % message)
        return p.returncode

    return update

def selection(column_names, title=None, boolstyle=None, editable=False, 
         select_col=None, sep='|', data=[]):
    """Present a list of items to select.
    
    This will raise a Zenity List Dialog populated with the colomns and rows 
    specified and return either the cell or row that was selected or None if 
    the user hit cancel.
    
    column_names - A tuple or list containing the names of the columns.
    title - The title of the dialog box.
    boolstyle - Whether the first columns should be a bool option ("checklist",
                "radiolist") or None if it should be a text field.
    editable - True if the user can edit the cells.
    select_col - The column number of the selected cell to return or "ALL" to 
                 return the entire row.
    sep - Token to use as the row separator when parsing Zenity's return. 
          Cells should not contain this token.
    data - A list or tuple of tuples that contain the cells in the row.  The 
           size of the row's tuple must be equal to the number of columns."""

    args = []
    for column in column_names:
        args.append('--column=%s' % column)
    
    if title:
        args.append('--title=%s' % title)
        args.append('--text=%s' % title)
    
    if boolstyle:
        if boolstyle != 'checklist' or boolstyle != 'radiolist':
            raise ValueError('"%s" is not a proper boolean column style.'
                             % boolstyle)
        args.append('--' + boolstyle)
    if editable:
        args.append('--editable')
    if select_col:
        args.append('--print-column=%s' % select_col)
    if sep != '|':
        args.append('--separator=%s' % sep)
    
    for datum in data:
        args.append(str(datum))
    
    p = run_zenity('--list', *args)

    if p.wait() == 0:
        return p.stdout.read().strip().split(sep)


def search(path,dir,i,taille):
    """ Fonction principale. Paramètres : chemin du fichier, dossier de travail, iteration n°, nombre de films.
         Cette fonction traite le chemin pour récupérer le nom du film, le formatte pour une recherche sur allociné.
         Puis récupère le film sur allociné et ouvre la page de ce film pour en tirer le genre du film."""
    name = path.replace(dir,"").lower() #Enleve le chemin absolue et le met en minuscules
    string = name_regexp1.sub("",name) #Retire l'extension du nom du fichier
    string = name_regexp2.sub("+",string) #Remplace les [.-_| ] par des '+' dans le nom de fichier
    
    if debug==True:
        print string
    the_url = "http://www.allocine.fr/recherche/?q={0}".format(string) #Lance la recherche sur Allociné
    req = urllib2.Request(the_url)

    try:
        handle = urllib2.urlopen(req)
    except IOError, e:
        if hasattr(e, 'reason'):
            print 'Nous avons échoué à joindre le serveur.'
            print 'Raison: ', e.reason
        elif hasattr(e, 'code'):
            print 'Le serveur n\'a pu satisfaire la demande. Niveau search(film)'
            print 'Code d\' erreur : ', e.code
    else:
        result = handle.read()

        if "<a href='/film/fichefilm_gen_cfilm" in result:
            id = result.split("<a href='/film/fichefilm_gen_cfilm=")[1].split(".html")[0] 
            #Recupere le 'id' du film sur Allociné

            lien = "http://www.allocine.fr/film/fichefilm_gen_cfilm={0}.html".format(id)
            if debug == True:
                print lien
            req = urllib2.Request(lien)

            try:
                handle = urllib2.urlopen(req)
            except IOError, e:
                if hasattr(e, 'reason'):
                    print 'Nous avons échoué à joindre le serveur.'
                    print 'Raison: ', e.reason
                elif hasattr(e, 'code'):
                    print 'Le serveur n\'a pu satisfaire la demande. Niveau search(genre)'
                    print 'Code d\' erreur : ', e.code
            else:
                result = handle.read()
                if '<span itemprop="genre">' in result:
                    #genre = result.split("<span itemprop=\"genre\">")[1].split("</span>")[0]
                    genres = genre_regexp.findall(result) #Recupere tous les genres proposés par Allociné
                    if automatique ==False and display==0 and len(genres) > 1:
                        genre = selection(['Genre'],"Genres pour "+name,data=genres)[0] #Demande à user de choisir le genre correspondant pour le film
                    else:
                        genre = genres[0]

                    if debug == True:
                        print genre
                        print i

                    if display == 0:
                        processus(float(i)/float(taille),"({0} / {1}) Ajouté à la liste {2}".format(i,taille,path+" ("+genre+")")) #Change le statut de la barre de progression
                    else:
                        print "({0} / {1}) Ajouté à la liste {2}".format(i,taille,path+" ("+genre+")")
                    ordonner(dir,path,genre,name)
                else:
                    if display == 0:
                        processus(float(i)/float(taille),"({0} / {1}) Impossible de trouver le genre pour {2}".format(i,taille,name))
                    else:
                        print "({0} / {1}) Impossible de trouver le genre pour {2}".format(i,taille,name)
        else:
            if display == 0:
                processus(float(i)/float(taille),"({0} / {1}) Impossible de trouver le film {2}".format(i,taille,name))
                answ = question("({0} / {1}) Impossible de trouver le film {2}.\nChoisir un genre parmi ceux existant ?".format(i,taille,name))
                if answ==True:
                    dirs = os.listdir(dir)
                    for indval in enumerate(dirs):
                        #print indval
                        if os.path.isfile(dir+dirs[indval[0]]):
                            del dirs[indval[0]]
                    #print dirs
                    genre = selection(['Genre'],"Genre pour "+name,data=dirs)[0] #Demande à user de choisir le genre correspondant pour le film
                    ordonner(dir,path,genre,name)
            else:
                print "({0} / {1}) Impossible de trouver le genre pour {2}".format(i,taille,name)

def ordonner(dir,path,genre,name):
    """ En paramètres : dossier de travail, chemin du fichier, genre du film, nom du film.
        Effectue le tri en fonction du genre du film """
    if genre not in os.listdir(dir):
        os.mkdir(dir+genre, 0775) #Créer le dossier du genre s'il n'éxiste pas
    os.rename(path,dir+genre+os.sep+name) #Déplace le fichier dans le dossier du genre
    #if display == 0:
        #info("Fichier %s déplacé avec succes" %name)
    #else:
        #print "Fichier %s déplacé avec succes" %name


if __name__ == "__main__":
    """ Fonction Main : recupere les arguments, liste les fichiers dans le repertoire choisi. Créer la liste des extensions. Et lance le traitement"""
    display = 0 #0: fenetre, 1: console
    debug = False
    extensions = ("avi","mp4","mpeg","divx","mkv","flv")
    extension_regexp = ""
    liste = []
    automatique = True

    if (len(sys.argv) >= 2) and (sys.argv[2] == "debug=1" or sys.argv[2] == "debug=True"):
        debug = True
        display = 1
        automatique = True

    if display == 0:
        dir = get_folder()
        dir += os.sep
    else:
        dir = sys.argv[1]

    try:
        j=0
        while j<len(extensions):
            liste += glob.glob(dir+'*.'+extensions[j])
            if j < len(extensions)-1:
                extension_regexp += extensions[j]+"|"
            else:
                extension_regexp += extensions[j]
            j += 1
        if debug==True:
            print extension_regexp
            print liste

    except IOError, e:
        if hasattr(e, 'reason'):
            print 'Le chemin est faux ou n\'existe pas.'
            print 'Raison: ', e.reason
        elif hasattr(e, 'code'):
            print 'Le serveur n\'a pu satisfaire la demande. Niveau main'
            print 'Code d\' erreur : ', e.code
    
    taille = len(liste)
    i = 0
    genre_regexp = re.compile("\<span itemprop=\"genre\"\>([\w\séèà-]+)\</span\>")
    name_regexp1 = re.compile(".("+extension_regexp+")")
    name_regexp2 = re.compile("[-_\|\.\s]")

    if display == 0:
        string = "Auteur : Hugo Rodde\nIl y a {0} films à traiter dans le dossier {1}.\nVoulez-vous procéder au rangement de vos films par Genre d'après Allociné ?".format(taille,dir)
        continuer = question(string)
        if continuer==True:
            mode = question("Le traitement est par défaut automatique. Voulez-vous passer en manuel ? C'est-à-dire choisir le genre de chaque film si plusieurs genres sont trouvés")
            if mode == True:
                automatique = False
            processus = process("Le traitement va commencer...",0,True)
            for file in liste:
                i = i+1
                search(file,dir,i,taille)
            info("Le travail est fini")
        else:
            info("Comme tu veux ...")
    else:
        print "Auteur : {0} <{1}>".format("Hugo Rodde","rodde.hugo@gmail.com")
        print "Il y a {0} films à traiter dans le dossier {1}. Voulez-vous procéder au rangement de vos films par Genre d'après Allociné ? (O/n)".format(taille,dir)

        continuer = raw_input()
        if continuer=="o" or continuer=="O":
            for file in liste:
                i = i+1
                search(file,dir,i,taille)
            print "Done !"
        else:
            print "Comme tu veux ..."
