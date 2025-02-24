import io
from flask import (
    flash, jsonify, 
    render_template, 
    send_file, redirect, 
    render_template, url_for, 
    render_template_string
    )
from mobilist.app import app, db
from reportlab.pdfgen import canvas
from datetime import datetime, date
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import spacy
from PyPDF2 import PdfReader
import ast
import webbrowser
nlp = spacy.load("fr_core_news_md")
from mobilist.app import app
from ...models.classes.User import User
from ...models.classes.TypeBien import TypeBien
from ...models.classes.Proprietaire import Proprietaire
from ...models.classes.Logement import Piece
from ...models.classes.Logement import LogementType
from ...models.classes.Logement import Logement
from ...models.classes.Justificatif import Justificatif
from ...models.classes.Categorie import Categorie
from ...models.classes.Logement import Bien
from ...models.classes.Logement import AVOIR
from ...models.classes.Avis import Avis
from sqlalchemy.sql.expression import func



def generate_pdf_tous_logements(proprio,logements) -> io.BytesIO:
    buffer = io.BytesIO()
    canva = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    # Fonction qui dessine des blocs gris avec du texte
    def draw_grey_box_with_text(canva, x, y, width, height, text, font="Helvetica", font_size=13):
        canva.setFillColorRGB(0.827, 0.827, 0.827)
        canva.rect(x, y, width, height, fill=1, stroke=0)
        canva.setFillColorRGB(0, 0, 0)
        canva.setFont(font, font_size)
        canva.drawString(x + 5, y + height / 2 - font_size / 2, text)
    # Titre 
    canva.setFillColorRGB(0.38, 0.169, 0.718)
    canva.setFont("Helvetica-Bold", 20)
    canva.drawCentredString(width / 2, y, "INVENTAIRE DES BIENS")
    y -= 1 * cm
    # Sous-titre
    canva.setFillColorRGB(0, 0, 0)
    canva.setFont("Helvetica-Bold", 15)
    canva.drawCentredString(width / 2, y, f"en date du {date.today()}")
    y -= 1.5 * cm
    # Valeur
    total_valeur = db.session.query(func.sum(Bien.prix)).filter(Bien.id_proprio == proprio.id_proprio).scalar()
    if total_valeur == None:
        total_valeur = 0
    canva.setFillColorRGB(0.792, 0.659, 1)
    canva.rect(20, y, width - 40, 1 * cm, fill=1, stroke=0)
    canva.setFillColorRGB(0, 0, 0)
    canva.setFont("Helvetica-Bold", 12)
    canva.drawString(25, y + 8, f"VALEUR TOTALE ESTIMÉE DE TOUS LES BIENS SANS VETUSTE: {total_valeur} €")
    y -= 1.5 * cm
    # Informations
    height_box = 1 * cm
    draw_grey_box_with_text(canva, 20, y-3, width - 40, height_box, f"NOM : {proprio.get_nom()} {proprio.get_prenom()}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-6, width - 40, height_box, f"MAIL : {proprio.get_mail()}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-9, width - 40, height_box, f"ANNÉE DU SINISTRE : {datetime.now().year}")
    y -= height_box
    # Parcours des pièces et des biens
    for loge in logements:
        if y < 3 * cm:
            canva.showPage()
            y = height - 2 * cm
        canva.setFont("Helvetica-Bold", 13)
        canva.drawString(1 * cm, y, f"{loge.nom_logement} ({loge.adresse})")
        y -= 1 * cm
        pieces = db.session.query(Piece).filter_by(id_logement=loge.id_logement).all()
        for p in pieces:
            if y < 3 * cm:  # Saut de page si besoin
                canva.showPage()
                y = height - 2 * cm
            canva.setFont("Helvetica-Bold", 12)
            canva.drawString(1 * cm, y, f"{p.get_nom_piece()}")
            canva.drawRightString(width - 6 * cm, y, "Prix neuf")
            canva.drawRightString(width - 2 * cm, y, f"Avec vétusté")
            y -= 0.7 * cm
            biens = db.session.query(Bien, Categorie).join(Categorie, Bien.id_cat == Categorie.id_cat) \
                .filter(Bien.id_piece == p.id_piece).all()
            biens_par_categorie = {}
            total_piece = 0
            for bien, categorie in biens:
                # vétusté = (âge de l'équipement/durée de vie estimée) x 100, ici on considère que la durée de vie = 10ans  (source : www.pap.fr)
                age_equipement = datetime.now().year - bien.date_achat.year
                vetuste = age_equipement / 10 * 100
                total_current_piece = bien.prix - vetuste
                if total_current_piece <= bien.prix:
                    total_current_piece = 0
                biens_par_categorie.setdefault(categorie.nom_cat, []).append((bien.nom_bien, bien.prix, total_current_piece))
                total_piece += total_current_piece
            for cat, items in biens_par_categorie.items():
                canva.setFont("Helvetica-Bold", 11)
                canva.drawString(2 * cm, y, f"{cat}")
                y -= 0.5 * cm
                canva.setFont("Helvetica", 10)
                for nom_bien, prix, vetuste in items:
                    canva.drawString(3 * cm, y, f"- {nom_bien}")
                    canva.drawRightString(width - 6 * cm, y, f"{prix} €")
                    canva.drawRightString(width - 2 * cm, y, f"{total_current_piece} €")
                    y -= 0.5 * cm
                    if y < 3 * cm:  # Saut de page si besoin
                        canva.showPage()
                        y = height - 2 * cm
                y -= 0.5 * cm  # Espace entre catégories
            canva.setFont("Helvetica-Bold", 11)
            canva.drawRightString(width - 2 * cm, y, f"Total : {total_piece}€")
            y -= 1 * cm  
            # Ligne de fin
            canva.line(1 * cm, y, width - 2 * cm, y)
            y -= 1 * cm        
    canva.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="inventaire_biens.pdf", mimetype="application/pdf")


def generate_pdf(proprio,logement_id,sinistre_annee,sinistre_type) -> io.BytesIO:
    buffer = io.BytesIO()
    canva = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    # Fonction qui dessine des blocs gris avec du texte
    def draw_grey_box_with_text(canva, x, y, width, height, text, font="Helvetica", font_size=13):
        canva.setFillColorRGB(0.827, 0.827, 0.827)
        canva.rect(x, y, width, height, fill=1, stroke=0)
        canva.setFillColorRGB(0, 0, 0)
        canva.setFont(font, font_size)
        canva.drawString(x + 5, y + height / 2 - font_size / 2, text)
    # Titre 
    canva.setFillColorRGB(0.38, 0.169, 0.718)
    canva.setFont("Helvetica-Bold", 20)
    canva.drawCentredString(width / 2, y, "INVENTAIRE DES BIENS")
    y -= 1 * cm
    # Sous-titre
    canva.setFillColorRGB(0, 0, 0)
    canva.setFont("Helvetica-Bold", 15)
    canva.drawCentredString(width / 2, y, f"en date du {date.today()}")
    y -= 1.5 * cm
    # Valeur totale
    total_valeur = db.session.query(func.sum(Bien.prix)).filter(Bien.id_logement == logement_id).scalar()
    if total_valeur == None:
        total_valeur = 0
    canva.setFillColorRGB(0.792, 0.659, 1)
    canva.rect(20, y, width - 40, 1 * cm, fill=1, stroke=0)
    canva.setFillColorRGB(0, 0, 0)
    canva.setFont("Helvetica-Bold", 12)
    canva.drawString(25, y + 8, f"VALEUR TOTALE ESTIMÉE DE TOUS LES BIENS SANS VETUSTE: {total_valeur} €")
    y -= 1.5 * cm
    # Informations
    height_box = 1 * cm
    draw_grey_box_with_text(canva, 20, y-3, width - 40, height_box, f"NOM : {proprio.get_nom()} {proprio.get_prenom()}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-6, width - 40, height_box, f"MAIL : {proprio.get_mail()}")
    y -= height_box
    adresse = db.session.query(Logement).filter_by(id_logement=logement_id).first().adresse
    draw_grey_box_with_text(canva, 20, y-9, width - 40, height_box, f"ADRESSE DU LOGEMENT : {adresse}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-12, width - 40, height_box, f"ANNÉE DU SINISTRE : {sinistre_annee}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-15, width - 40, height_box, f"TYPE DE SINISTRE : {sinistre_type}")
    y -= 1.5 * cm
    # Parcours des pièces et des biens
    pieces = db.session.query(Piece).filter_by(id_logement=logement_id).all()
    for p in pieces:
        if y < 3 * cm:  # Saut de page si besoin
            canva.showPage()
            y = height - 2 * cm
        canva.setFont("Helvetica-Bold", 12)
        canva.drawString(1 * cm, y, f"{p.get_nom_piece()}")
        canva.drawRightString(width - 6 * cm, y, "Prix neuf")
        canva.drawRightString(width - 2 * cm, y, f"Avec vétusté")
        y -= 0.7 * cm
        biens = db.session.query(Bien, Categorie).join(Categorie, Bien.id_cat == Categorie.id_cat) \
            .filter(Bien.id_piece == p.id_piece).all()
        biens_par_categorie = {}
        total_piece = 0
        for bien, categorie in biens:
            # vétusté = (âge de l'équipement/durée de vie estimée) x 100, ici on considère que la durée de vie = 10ans  (source : www.pap.fr)
            age_equipement = datetime.now().year - bien.date_achat.year
            vetuste = age_equipement / 10 * 100
            total_current_piece = bien.prix - vetuste
            if total_current_piece <= bien.prix:
                total_current_piece = 0
            biens_par_categorie.setdefault(categorie.nom_cat, []).append((bien.nom_bien, bien.prix, total_current_piece))
            total_piece += total_current_piece       
        for cat, items in biens_par_categorie.items():
            canva.setFont("Helvetica-Bold", 11)
            canva.drawString(2 * cm, y, f"{cat}")
            y -= 0.5 * cm
            canva.setFont("Helvetica", 10)
            for nom_bien, prix, vetuste in items:
                canva.drawString(3 * cm, y, f"- {nom_bien}")
                canva.drawRightString(width - 6 * cm, y, f"{prix} €")
                canva.drawRightString(width - 2 * cm, y, f"{total_current_piece} €")
                y -= 0.5 * cm
                if y < 3 * cm:  # Saut de page si besoin
                    canva.showPage()
                    y = height - 2 * cm
            y -= 0.5 * cm  # Espace entre catégories
        canva.setFont("Helvetica-Bold", 11)
        canva.drawRightString(width - 2 * cm, y, f"Total : {total_piece}€")
        y -= 1 * cm
        # Ligne de fin
        canva.line(1 * cm, y, width - 2 * cm, y)
        y -= 1 * cm        
    canva.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="inventaire_biens.pdf", mimetype="application/pdf")

