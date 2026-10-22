import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
import plotly.express as px
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
import plotly.express as px
import plotly

from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

def create_styles():
    """Crea los estilos para el PDF"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='TitleStyle',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubtitleStyle',
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='BodyStyle',
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=10,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='HeaderStyle',
        fontSize=12,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    ))
    
    return styles


def write_chillhours_pdf(opt):
    """Genera un PDF para reporte de Horas Frío"""
    
    styles = create_styles()
    
    # Crear documento
    doc = SimpleDocTemplate(
        opt.path_save,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    story = []
    
    # Título
    title = f"Reporte de Horas Frío N° {opt.n_report}"
    story.append(Paragraph(title, styles['TitleStyle']))
    
    # Subtítulo con campo
    subtitle = f"Campo: {opt.data_field.replace('-', ' ').title()}"
    story.append(Paragraph(subtitle, styles['SubtitleStyle']))
    
    story.append(Spacer(1, 20))
    
    # Información del reporte
    info_data = [
        ["Fecha de inicio:", f"{opt.day_in}/{opt.month_in}/{opt.year_in}"],
        ["Fecha de término:", f"{opt.day_out}/{opt.month_out}/{opt.year_out}"],
        ["Zona:", str(opt.zone)],
        ["Fecha de generación:", datetime.now().strftime("%d/%m/%Y %H:%M")],
    ]
    
    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    
    story.append(Spacer(1, 30))
    
    # Descripción
    description = """
    Para la evaluación de riesgos y proyecciones de eventos climáticos de interés para la producción 
    de cereza en la región de O'Higgins se ha dispuesto de la evaluación de parámetros climáticos.
    
    El historial de temperaturas históricas es registrado a través de sensores ambientales 
    distribuidos en diferentes sectores de la zona de producción.
    
    La revisión de los datos climáticos considera la revisión de la temperatura promedio del aire 
    como también la evaluación de las variables agroclimáticas necesarias para los frutales de 
    hoja caduca como lo son las Horas de Frío.
    """
    story.append(Paragraph(description, styles['BodyStyle']))
    
    story.append(Spacer(1, 20))
    
    # Nota sobre gráficos
    note = """
    <b>Nota:</b> Los gráficos de temperatura y horas frío acumuladas se encuentran disponibles 
    en la visualización web del reporte.
    """
    story.append(Paragraph(note, styles['BodyStyle']))
    
    # Construir PDF
    doc.build(story)
    print(f"PDF generado exitosamente: {opt.path_save}")


def write_chillportions_pdf(opt):
    """Genera un PDF para reporte de Porciones Frío"""
    
    styles = create_styles()
    
    # Crear documento
    doc = SimpleDocTemplate(
        opt.path_save,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    story = []
    
    # Título
    title = f"Reporte de Porciones Frío N° {opt.n_report}"
    story.append(Paragraph(title, styles['TitleStyle']))
    
    # Subtítulo con campo
    subtitle = f"Campo: {opt.data_field.replace('-', ' ').title()}"
    story.append(Paragraph(subtitle, styles['SubtitleStyle']))
    
    story.append(Spacer(1, 20))
    
    # Información del reporte
    info_data = [
        ["Fecha de inicio:", f"{opt.day_in}/{opt.month_in}/{opt.year_in}"],
        ["Fecha de término:", f"{opt.day_out}/{opt.month_out}/{opt.year_out}"],
        ["Zona:", str(opt.zone)],
        ["Fecha de generación:", datetime.now().strftime("%d/%m/%Y %H:%M")],
    ]
    
    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    
    story.append(Spacer(1, 30))
    
    # Descripción
    description = """
    Para la evaluación de riesgos y proyecciones de eventos climáticos de interés para la producción 
    de cereza en la región de O'Higgins se ha dispuesto de la evaluación de parámetros climáticos.
    
    El modelo de Porciones Frío (Chill Portions) es un método más preciso para calcular la acumulación 
    de frío en frutales de hoja caduca, considerando las fluctuaciones de temperatura durante el 
    período de dormancia.
    
    Este modelo es particularmente útil para predecir la ruptura de dormancia y planificar las 
    actividades de manejo del huerto.
    """
    story.append(Paragraph(description, styles['BodyStyle']))
    
    story.append(Spacer(1, 20))
    
    # Nota sobre gráficos
    note = """
    <b>Nota:</b> Los gráficos de temperatura y porciones frío acumuladas se encuentran disponibles 
    en la visualización web del reporte.
    """
    story.append(Paragraph(note, styles['BodyStyle']))
    
    # Construir PDF
    doc.build(story)
    print(f"PDF generado exitosamente: {opt.path_save}")


def main(opt):
    """Función principal que selecciona el tipo de reporte"""
    if opt.type_data == "chillhours":
        write_chillhours_pdf(opt)
    elif opt.type_data == "chillportions":
        write_chillportions_pdf(opt)
    else:
        print(f"Tipo de datos no reconocido: {opt.type_data}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='write_agroclimate_pdf.py',
        description='Genera PDFs para reportes agroclimáticos (horas frío y porciones frío).'
    )
    
    parser.add_argument('--path-save', type=str, required=True,
                        help='Ruta donde guardar el PDF generado.')
    parser.add_argument('--data-field', type=str, required=True,
                        help='Nombre del campo.')
    parser.add_argument('--zone', type=str, default='1',
                        help='Zona del campo.')
    parser.add_argument('--day-in', type=int, required=True,
                        help='Día de inicio.')
    parser.add_argument('--month-in', type=int, required=True,
                        help='Mes de inicio.')
    parser.add_argument('--year-in', type=int, required=True,
                        help='Año de inicio.')
    parser.add_argument('--day-out', type=int, required=True,
                        help='Día de término.')
    parser.add_argument('--month-out', type=int, required=True,
                        help='Mes de término.')
    parser.add_argument('--year-out', type=int, required=True,
                        help='Año de término.')
    parser.add_argument('--n-report', default='1', type=str,
                        help='Número de reporte.')
    parser.add_argument('--type-data', default='chillhours',
                        choices=['chillhours', 'chillportions'],
                        type=str, help='Tipo de reporte a generar.')
    
    opt = parser.parse_args()
    main(opt)
