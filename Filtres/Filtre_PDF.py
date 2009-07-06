#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre_PDF - ExeFilter

Ce module contient la classe L{Filtre_PDF.Filtre_PDF},
pour filtrer les documents PDF.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://admisource.gouv.fr/projects/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
@author: U{Tanguy Vinceleux<mailto:tanguy.vinceleux(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008 (modifications PL apres v1.1.0)

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 1.02

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2008-03-24"
__version__ = "1.02"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008 (PL changes after v1.1.0)
# Auteurs:
# - Philippe Lagadec (PL) - philippe.lagadec(a)laposte.net
# - Arnaud Kerr�neur (AK) - arnaud.kerreneur(a)dga.defense.gouv.fr
# - Tanguy Vinceleux (TV) - tanguy.vinceleux(a)dga.defense.gouv.fr
#
# Ce logiciel est r�gi par la licence CeCILL soumise au droit fran�ais et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL telle que diffus�e par le CEA, le CNRS et l'INRIA
# sur le site "http://www.cecill.info". Une copie de cette licence est jointe
# dans les fichiers Licence_CeCILL_V2-fr.html et Licence_CeCILL_V2-en.html.
#
# En contrepartie de l'accessibilit� au code source et des droits de copie,
# de modification et de redistribution accord�s par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limit�e.  Pour les m�mes raisons,
# seule une responsabilit� restreinte p�se sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les conc�dants successifs.
#
# A cet �gard  l'attention de l'utilisateur est attir�e sur les risques
# associ�s au chargement,  � l'utilisation,  � la modification et/ou au
# d�veloppement et � la reproduction du logiciel par l'utilisateur �tant
# donn� sa sp�cificit� de logiciel libre, qui peut le rendre complexe �
# manipuler et qui le r�serve donc � des d�veloppeurs et des professionnels
# avertis poss�dant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invit�s � charger  et  tester  l'ad�quation  du
# logiciel � leurs besoins dans des conditions permettant d'assurer la
# s�curit� de leurs syst�mes et ou de leurs donn�es et, plus g�n�ralement,
# � l'utiliser et l'exploiter dans les m�mes conditions de s�curit�.
#
# Le fait que vous puissiez acc�der � cet en-t�te signifie que vous avez
# pris connaissance de la licence CeCILL, et que vous en avez accept� les
# termes.

#------------------------------------------------------------------------------
# HISTORIQUE:
# 08/06/2005 v0.01 TV: - 1�re version
# 2005-2006  PL,TV,AK: - evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2008-02-19 v1.01 PL: - licence CeCILL
#                      - ajout suppression de mots-cles actifs (Javascript, ...)
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
#                      - simplification dans nettoyer() en appelant resultat_*

# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

import os, tempfile
import RechercherRemplacer

# modules du projet:
from commun import *
import Filtre, Resultat, Parametres


#=== CONSTANTES ===============================================================



#=== FONCTIONS ================================================================



#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe FILTRE_PDF
#-------------------
class Filtre_PDF (Filtre.Filtre):
    """
    classe pour un filtre de fichiers PDF.

    un objet Filtre sert � reconna�tre le format d'un fichier et �
    nettoyer le code �ventuel qu'il contient. La classe Filtre_PDF
    correspond aux fichiers images PDF.

    @cvar nom: Le nom detaill� du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre
    """

    nom = _(u"Document PDF")
    extensions = [".pdf"]
    format_conteneur = False
    extractible = False
    nettoyable = True

    # date et version d�finies � partir de celles du module
    date = __date__
    version = __version__

    def __init__ (self, politique, parametres=None):
        """Constructeur d'objet Filtre_PDF.

        parametres: dictionnaire pour fixer les param�tres du filtre
        """
        # on commence par appeler le constructeur de la classe de base
        Filtre.Filtre.__init__(self, politique, parametres)
        # ensuite on ajoute les param�tres par d�faut
        Parametres.Parametre(u"supprimer_javascript", bool,
            nom=u"Supprimer le code Javascript",
            description=u"Supprimer tout code Javascript, qui peut declencher "
                        +"des actions a l'insu de l'utilisateur.",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"supprimer_embeddedfile", bool,
            nom=u"Supprimer les fichiers inclus",
            description=u"Supprimer tout fichier inclus, qui peut camoufler "
                        +"du code executable.",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"supprimer_fileattachment", bool,
            nom=u"Supprimer les fichiers attaches",
            description=u"Supprimer tout fichier attache, qui peut camoufler "
                        +"du code executable.",
            valeur_defaut=True).ajouter(self.parametres)

    def reconnait_format(self, fichier):
        """
        analyse le format du fichier, et retourne True s'il correspond
        au format recherch�, False sinon.
        """
        debut = fichier.lire_debut()
        # Un fichier PDF bien form� doit obligatoirement commencer par "%PDF-"
        # (en fait Acrobat accepte jusqu'� 1019 caract�res quelconques
        # avant, mais ce n'est pas la structure classique d'un PDF...)
        if debut.startswith("%PDF-"):
            return True

    def nettoyer (self, fichier):
        """
        analyse et modifie le fichier pour supprimer tout code
        ex�cutable qu'il peut contenir, si cela est possible.
        Retourne un code r�sultat suivant l'action effectu�e.
        """
        # liste de motifs pour nettoyer certains mots cles PDF:
        motifs = []
        if self.parametres["supprimer_javascript"].valeur == True:
            motifs.append( RechercherRemplacer.Motif(case_sensitive=False,
                regex=r'/Javascript', remplacement='/NOjvscript'))
        if self.parametres["supprimer_embeddedfile"].valeur == True:
            motifs.append( RechercherRemplacer.Motif(case_sensitive=False,
                regex=r'/EmbeddedFile', remplacement='/NO_EmbedFile'))
        if self.parametres["supprimer_fileattachment"].valeur == True:
            motifs.append( RechercherRemplacer.Motif(case_sensitive=False,
                regex=r'/FileAttachment', remplacement='/NOFileAttachmt'))
        if len(motifs)>0:
            # creation d'un nouveau fichier temporaire
            f_temp, chem_temp = tempfile.mkstemp(dir=self.politique.parametres['rep_temp'].valeur)
            Journal.info2 (u"Fichier temporaire: %s" % chem_temp)
            f_dest = os.fdopen(f_temp, 'wb')
            # on ouvre le fichier source
            f_src = open(fichier.copie_temp(), 'rb')
            Journal.info2 (u"Nettoyage PDF par remplacement de chaine")
            n = RechercherRemplacer.rechercherRemplacer(motifs=motifs,
                fich_src=f_src, fich_dest=f_dest, taille_identique=True, controle_apres=True)
            f_src.close()
            f_dest.close()
            if n:
                Journal.info2 (u"Des objets PDF actifs ont ete trouves et desactives.")
                # Le fichier nettoye, on remplace la copie temporaire:
                fichier.remplacer_copie_temp(chem_temp)
                return self.resultat_nettoye(fichier)
                #return Resultat.Resultat(Resultat.NETTOYE,
                #    [self.nom + " : objets PDF actifs supprim�s"], fichier)
            else:
                # pas de contenu actif
                Journal.info2 (u"Aucun contenu PDF actif n'a ete trouve.")
                # on efface le ficher temporaire:
                os.remove(chem_temp)
                return self.resultat_accepte(fichier)
        else:
            resultat = self.resultat_accepte(fichier)
        return resultat


