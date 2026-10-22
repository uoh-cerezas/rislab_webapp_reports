import os
import json
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, StyleSheet1, _baseFontNameB
from logging import raiseExceptions

import plot_fields_utils as pfu


def filter_data_gps_positions(data):
    lat, lon = [], []
    for location in data:
        positions = location.split(',')
        lat += [float(positions[0].replace('(', ''))]
        lon += [float(positions[1].replace(')', ''))]
    array = np.stack([lat, lon], axis=1)
    return array

def save_image_file(field_type,path_counts,type_display='density'):

    # if os.path.isfile(path_locations):
    # locations = pd.read_excel(path_locations)
    # cols = locations.columns
    # new_cols = []
    # for col in cols:
    #     new_cols += [col.replace(' ', '')]
    #
    # locations.columns = new_cols
    counts = pd.read_excel(path_counts)

    new_cols = []
    cols = counts.columns
    for col in cols:
        new_cols += [col.replace(' ', '')]

    counts.columns = new_cols

    # merged_df = pd.merge(locations, counts, left_on=['Cuartel', 'Zona', 'Variedad', 'Planta'],
    #                      right_on=['Cuartel', 'Zona', 'Variedad', 'Planta'], how='inner')
    if type_display == 'density':
        values = counts['Estimados'].values
    else:
        values = counts['Madurez'].values * 100
    if field_type == "fic2-rengo-agritorre":
        border, positions = pfu.get_la_torre_points()
    elif field_type == "fic2-graneros-agrofurore":
        border, positions = pfu.get_graneros_points()
    elif field_type == "agricura":
        border, positions = pfu.get_agricura_points()
    elif field_type == 'fic2-rengo-donajaviera':
        border, positions = pfu.get_dona_javiera_rengo_c2()
    elif field_type == 'fic2-rengo-elperal':
        border, positions = pfu.get_el_peral_rengo_C3()
    elif field_type == 'fic2-rengo-eltotoral':
        border, positions = pfu.get_el_totoral_rengo_c2()
    elif field_type == 'fic2-peumo-greenex':
        border, positions = pfu.get_greenex_points()
    elif field_type == 'fic2-paine-neltume':
        border, positions = pfu.get_ceaf_points()
    else:
        print("Field type not recognized")
        # plt.axis('off')
        # plt.savefig('{:s}.jpeg'.format(field_type))
        return
    data_pos = counts['Pos'].values

    data_pos = filter_data_gps_positions(data_pos)
    data_pos = pfu.transform_locations(data_pos)
    plt.figure(figsize=(9, 9))
    pfu.plot_data_in_field(data_pos, values, positions, neighbors=4,type_display=type_display)
    plt.axis('off')
    output_dir = Path(path_counts).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / f'{field_type}.jpeg')
    plt.savefig('{:s}_{:s}.jpeg'.format(field_type,type_display))
    # else:
    #     print("Path location not recognized : {}".format(path_locations))

def check_type(objects_values):
    result = []
    for obj in objects_values:
        if type(obj) == int:
            result += ["{:d}".format(obj)]
        elif type(obj) == float:
            result += ["{:.3f}".format(obj)]
        elif type(obj) == str:
            result += ["{:s}".format(obj)]
        else:
            result += ["{}".format(obj)]
    return result

def get_info_data(path_images,field_type):
    draw_locations = True
    if field_type == 'graneros' :
        path_client_logo = os.path.join(path_images, 'logo_fic.png')
        dim_logo = [450, 50]
        name_entity = "Agrícola Agrofurore Limitada"
        region_info = "Graneros, Región del Libertador Bernardo O’Higgins"

    elif field_type == 'fic2-graneros-agrofurore':
        path_client_logo = os.path.join(path_images, 'logo_fic.png')
        dim_logo = [450, 50]
        name_entity = "Agrícola Agrofurore Limitada"
        region_info = "Graneros, Región del Libertador Bernardo O’Higgins"
    elif field_type == "fic2-rengo-agritorre":
        path_client_logo = os.path.join(path_images, 'rengo-agritorre.png')
        dim_logo = [400, 50]
        name_entity = "Agrícola La Torre S.A."
        region_info = "La Chimba, Rengo, Región del Libertador Bernardo O’Higgins"
    elif field_type == "greenex":
        path_client_logo = os.path.join(path_images, 'peumo-greenex.png')
        dim_logo = [450, 50]
        name_entity = "Agrícola Greenex S.A."
        region_info = "Codegua, Región del Libertador Bernardo O’Higgins"
    elif field_type == "ceaf":
        path_client_logo = os.path.join(path_images, 'rengo-ceaf.png')
        dim_logo = [450, 50]
        name_entity = "Centro de Estudios Avanzados en Fruticultura"
        region_info = "Rengo, Región del Libertador Bernardo O’Higgins"
    elif field_type == "liceo_sf":
        path_client_logo = os.path.join(path_images, 'logo_fic.png')
        dim_logo = [350, 50]
        name_entity = 'Liceo Agrícola El Carmen'
        region_info = "San Fernando, Rengo, Región del Libertador Bernardo O’Higgins"
    elif field_type == "fic2-rengo-donajaviera":
        path_client_logo = os.path.join(path_images, 'logo_fic.png')
        dim_logo = [350, 50]
        name_entity = 'DOÑA JAVIERA SA.'
        region_info = "DOÑA JAVIERA SA., Región del Libertador Bernardo O’Higgins"
    elif field_type == "fic2-rengo-elperal":
        path_client_logo = os.path.join(path_images, 'logo_fic.png')
        dim_logo = [350, 50]
        name_entity = 'Fundo El Peral'
        region_info = "Fundo El Peral, Rengo, Región del Libertador Bernardo O’Higgins"
    elif field_type == "fic2-rengo-eltotoral":
        path_client_logo = os.path.join(path_images, 'logo_fic.png')
        dim_logo = [350, 50]
        name_entity = 'El Totoral-Predio Agricola'
        region_info = "El Totoral-Predio Agricola, Rengo, Región del Libertador Bernardo O’Higgins"

    elif field_type == 'agricura':
        path_client_logo = os.path.join(path_images, 'rengo-agricura.png')
        dim_logo = [450, 50]
        name_entity = "Agrícola Agricura S.A."
        region_info = "Rengo, Región del Libertador Bernardo O’Higgins"

    elif field_type == 'fic2-paine-neltume':
        path_client_logo = os.path.join(path_images, 'logo_fic.png')
        dim_logo = [350, 50]
        name_entity = "Agrícola Neltume spa"
        region_info = "Paine, Región Metropolitana"
    else:
        path_client_logo = os.path.join(path_images, 'logo_fic.png')
        dim_logo = [350, 50]
        name_entity = "Empresa Agricola"
        region_info = "Región del Libertador Bernardo O’Higgins"
        draw_locations = False


    return path_client_logo, dim_logo, name_entity, region_info, draw_locations

def generate_report_pdf_cherries(field_name, path_records, pdf_file, path_images, n_report, date_recording, date_report,
                                 n_tree_per_recording = 11):

    doc = SimpleDocTemplate(pdf_file, pagesize=letter)

    # List to hold PDF elements
    elements = []

    # Styles for text
    styles = getSampleStyleSheet()
    path_client_logo, dim_logo, name_entity, region_info, draw_locations = get_info_data(path_images, field_name)
    try:
        img = Image(path_client_logo, width=dim_logo[0], height=dim_logo[1])
        elements.append(img)
    except IOError:
        elements.append(Paragraph("Image not found: " + path_images, styles["Normal"]))

    data = pd.read_excel(path_records)
    if draw_locations:
        draw_locations = "Pos" in data.columns

    mean = data['Estimados'].mean()
    data["Estimados"] = data["Estimados"].astype('int')
    data["Estimados min"] = data["Estimados min"].astype('int')
    data["Estimados max"] = data["Estimados max"].astype('int')
    data["Madurez"] *= 100
    data["Rango Cerezas"] = ["{:d} - {:d}".format(min_v, max_valur) for (min_v, max_valur) in
                            zip(data["Estimados min"].values,
                                data["Estimados max"].values)]

    data = data[['Cuartel', 'Zona', 'Variedad', 'Planta', 'Roja',
                 'Naranja',"Verde", "Madurez", 'Estimados', 'Rango Cerezas']]

    data.columns = ['Cuartel', 'Zona', 'Variedad', 'Planta', 'Roja',
                    'Naranja',"Verde","Madurez [%]", 'Conteo de Cerezas', 'Rango Cerezas']

    counts = len(data) * n_tree_per_recording

    data = data.sort_values(["Planta", "Cuartel", "Zona", "Variedad"])
    elements.append(Spacer(1, 12))
    paragraph = Paragraph("UOH Cerezas - Reporte {:d} de Conteo Automatizado de Cerezas".format(n_report),
                          styles["Title"])
    elements.append(paragraph)
    elements.append(Spacer(1, 12))


    paragraph = Paragraph(name_entity, ParagraphStyle(name='Subtitle',
                                                      parent=styles['Normal'],
                                                      alignment=TA_CENTER,
                                                      fontName=_baseFontNameB,
                                                      fontSize=14,
                                                      leading=18,
                                                      spaceBefore=12))

    elements.append(paragraph)
    elements.append(Spacer(1, 12))



    paragraph = Paragraph(region_info, styles["BodyText"])

    elements.append(paragraph)
    elements.append(Spacer(2, 12))
    paragraph = Paragraph("Resumen:", styles["BodyText"])
    elements.append(paragraph)
    paragraph = Paragraph("Para la evaluación de riesgos y estimación de la producción de cereza en la Región del "
                          "Libertador Bernardo O’Higgins, se han contabilizado los datos del año 2025 en su predio. Se contabilizaron"
                          " {:d} árboles dando una cantidad promedio de {:.1f} cerezas por árbol. Para más detalle ver tabla 1.".format(
        counts,
        mean
        ),
                          styles["BodyText"])

    elements.append(paragraph)
    elements.append(Spacer(2, 12))

    style_caption = ParagraphStyle(name='Caption Table',
                                   parent=styles['Normal'],
                                   alignment=TA_CENTER,
                                   spaceBefore=6)

    unique_fields = list(data["Cuartel"].unique())

    generate_tables(data, date_recording, elements, style_caption, unique_fields,categories=['Roja','Naranja',"Verde"])
    if draw_locations:
        paragraph = Paragraph("A continuación se muestras un mapa de calor que representa las zonas de mayor y"
                              " menor concentración de cerezas. ", styles["BodyText"])

        elements.append(paragraph)
        elements.append(Spacer(2, 12))
        paragraph = Paragraph(
            "Imagen 1: Mapa de densidad de cerezas en el campo. Se pueden distinguir zonas  de baja concentración de cerezas (azul y celeste) de zonas "
            "de alta concentracion (rojo y amarillo). Se estima valores de densidad a partir de las grabaciones realizadas en campo "
            "(arboles de control) el cual es extrapolado a regiones del predio que no hayan sido grabadas.", style_caption)

        elements.append(paragraph)
        elements.append(Spacer(1, 12))

        image_path = '{:s}_density.jpeg'.format(field_name)  # Put an actual path here
        try:
            img = Image(image_path, width=400, height=400)
            elements.append(img)
        except IOError:
            elements.append(Paragraph("Image not found: " + image_path, styles["Normal"]))
        elements.append(PageBreak())
    paragraph = Paragraph("Metodologia de procesamiento:", styles["Heading2"])
    elements.append(paragraph)
    f = open("resources/explicacion.txt")
    text_explanation = f.readline()
    paragraph = Paragraph(text_explanation, styles["BodyText"])
    elements.append(paragraph)
    elements.append(Spacer(1, 12))

    image_path = os.path.join(path_images, 'camara_recording.jpg')  # Put an actual path here
    img = Image(image_path, width=125, height=200)
    elements.append(img)
    elements.append(Spacer(1, 12))
    paragraph = Paragraph("Reconocimiento:", styles["BodyText"])
    elements.append(paragraph)
    elements.append(Spacer(1, 12))
    paragraph = Paragraph(
        "Financiamiento por parte del Gobierno Regional para el desarollo del Proyecto FIC 40027312-0 `Transferencia y adopción de tecnologías para la gestión de riesgo en el "
        "proceso productivo de la cereza: hacia una agricultura de precisión para la Región de O’Higgins`. "
        , styles["BodyText"])
    elements.append(paragraph)
    elements.append(Spacer(6, 12))

    paragraph = Paragraph(
        "Fecha de elaboración del reporte: {:02d} de {:02d} del {:d}".format(*date_report),
        styles["BodyText"])
    elements.append(paragraph)
    # Build the PDF
    doc.build(elements)


def generate_report_pdf_buds(field_name, path_records, pdf_file, path_images, n_report, date_recording, date_report,
                             n_tree_per_recording = 11, ):

    doc = SimpleDocTemplate(pdf_file, pagesize=letter)

    # List to hold PDF elements
    elements = []

    # Styles for text
    styles = getSampleStyleSheet()
    path_client_logo, dim_logo, name_entity, region_info, draw_locations = get_info_data(path_images, field_name)

    try:
        img = Image(path_client_logo, width=dim_logo[0], height=dim_logo[1])
        elements.append(img)
    except IOError:
        elements.append(Paragraph("Image not found: " + path_images, styles["Normal"]))

    data = pd.read_excel(path_records)
    if draw_locations:
        draw_locations = "Pos" in data.columns

    mean = data['Estimados'].mean()
    data["Estimados"] = data["Estimados"].astype('int')
    data["Estimados min"] = data["Estimados min"].astype('int')
    data["Estimados max"] = data["Estimados max"].astype('int')
    data["Madurez"] *= 100
    data["Rango Dardos"] = ["{:d} - {:d}".format(min_v, max_valur) for (min_v, max_valur) in
                            zip(data["Estimados min"].values,
                                data["Estimados max"].values)]

    data = data[['Cuartel', 'Zona', 'Variedad', 'Planta', 'Dardos',
                 'Flores',"Madurez", 'Estimados', 'Rango Dardos']]
    data.columns = ['Cuartel', 'Zona', 'Variedad', 'Planta', 'Dardos',
                    'Flores',"Madurez [%]", 'Conteo de Dardos', 'Rango Dardos']

    counts = len(data) * n_tree_per_recording

    data = data.sort_values(["Planta", "Cuartel", "Zona", "Variedad"])
    elements.append(Spacer(1, 12))
    paragraph = Paragraph("UOH Cerezas - Reporte {:d} de Conteo Automatizado de Yemas y Dardos".format(n_report),
                          styles["Title"])
    elements.append(paragraph)
    elements.append(Spacer(1, 12))


    paragraph = Paragraph(name_entity, ParagraphStyle(name='Subtitle',
                                                      parent=styles['Normal'],
                                                      alignment=TA_CENTER,
                                                      fontName=_baseFontNameB,
                                                      fontSize=14,
                                                      leading=18,
                                                      spaceBefore=12))

    elements.append(paragraph)
    elements.append(Spacer(1, 12))



    paragraph = Paragraph(region_info, styles["BodyText"])

    elements.append(paragraph)
    elements.append(Spacer(2, 12))
    paragraph = Paragraph("Resumen:", styles["BodyText"])
    elements.append(paragraph)
    paragraph = Paragraph("Para la evaluación de riesgos y estimación de la producción de cereza en la Región del "
                          "Libertador Bernardo O’Higgins, se han contabilizado los datos del año 2025 en su predio. Se contabilizaron"
                          " {:d} árboles dando una cantidad promedio de {:.1f} dardos por árbol. Para más detalle ver tabla 1.".format(
        counts,
        mean
        ),
                          styles["BodyText"])

    elements.append(paragraph)
    elements.append(Spacer(2, 12))

    style_caption = ParagraphStyle(name='Caption Table',
                                   parent=styles['Normal'],
                                   alignment=TA_CENTER,
                                   spaceBefore=6)

    unique_fields = list(data["Cuartel"].unique())

    generate_tables(data, date_recording, elements, style_caption, unique_fields)
    if draw_locations:
        paragraph = Paragraph("A continuación se muestras un mapa de calor que representa las zonas de mayor y"
                              " menor concentración de dardos. ", styles["BodyText"])

        elements.append(paragraph)
        elements.append(Spacer(2, 12))
        paragraph = Paragraph(
            "Imagen 1: Mapa de densidad de dardos en el campo. Se pueden distinguir zonas  de baja concentración de dardos (azul y celeste) de zonas "
            "de alta concentracion (rojo y amarillo). Se estima valores de densidad a partir de las grabaciones realizadas en campo "
            "(arboles de control) el cual es extrapolado a regiones del predio que no hayan sido grabadas.", style_caption)

        elements.append(paragraph)
        elements.append(Spacer(1, 12))

        image_path = '{:s}_density.jpeg'.format(field_name)  # Put an actual path here
        try:
            img = Image(image_path, width=400, height=400)
            elements.append(img)
        except IOError:
            elements.append(Paragraph("Image not found: " + image_path, styles["Normal"]))
        elements.append(PageBreak())
    paragraph = Paragraph("Metodologia de procesamiento:", styles["Heading2"])
    elements.append(paragraph)
    f = open("resources/explicacion.txt")
    text_explanation = f.readline()
    paragraph = Paragraph(text_explanation, styles["BodyText"])
    elements.append(paragraph)
    elements.append(Spacer(1, 12))

    image_path = os.path.join(path_images, 'camara_recording.jpg')  # Put an actual path here
    img = Image(image_path, width=125, height=200)
    elements.append(img)
    elements.append(Spacer(1, 12))
    paragraph = Paragraph("Reconocimiento:", styles["BodyText"])
    elements.append(paragraph)
    elements.append(Spacer(1, 12))
    paragraph = Paragraph(
        "Financiamiento por parte del Gobierno Regional para el desarollo del Proyecto FIC 40027312-0 `Transferencia y adopción de tecnologías para la gestión de riesgo en el "
        "proceso productivo de la cereza: hacia una agricultura de precisión para la Región de O’Higgins`. "
        , styles["BodyText"])
    elements.append(paragraph)
    elements.append(Spacer(6, 12))

    paragraph = Paragraph(
        "Fecha de elaboración del reporte: {:02d} de {:02d} del {:d}".format(*date_report),
        styles["BodyText"])
    elements.append(paragraph)
    # Build the PDF
    doc.build(elements)


def generate_tables(data, date_recording, elements, style_caption, unique_fields, categories=['Dardos', 'Flores']):
    for i, c in enumerate(unique_fields):
        paragraph = Paragraph("Tabla {:d}: Conteo asistido mediante inteligencia artificial de yemas, "
                              "dardos, hojas y flores en {:s}. ({:02d} de {:02d} {:d}).".format(i + 1, c,
                                                                                                *date_recording),
                              style_caption)
        elements.append(paragraph)
        elements.append(Spacer(1, 12))

        # Convert DataFrame to a list of lists (including header
        subdata = data[data['Cuartel'] == c]
        subdata = subdata.copy()
        ratios = np.sum(subdata[categories].values, axis=1)
        for cat in categories:
            subdata[cat] /= ratios

        table_data = [subdata.columns.tolist()] + list(map(check_type, subdata.values.tolist()))

        table = Table(table_data)

        # Table style
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgray),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))


def main(opt):
    field_type = opt.data_field #
    path_records = opt.path_predictions # 'reporte_{:s}_junio_videos.xlsx'.format(field_type)
    day, month, year = opt.day, opt.month, opt.year
    type_data = opt.type_data
    day_report, month_report, year_report = [int(value) for value in datetime.today().strftime('%d-%m-%Y').split('-')]
    # path_locations = opt.path_locations
    path_images = 'resources/'
    n_report = opt.n_report
    try:
        save_image_file(field_type,path_records)
        # save_image_file(field_type,path_records,'maturity')
    except:
        print("Error: no se pudo generar el archivo de imagenes.")
    if type_data == 'buds':
        generate_report_pdf_buds(field_type, path_records, opt.path_save, path_images, n_report, date_recording=[day, month, year],
                                 date_report = [day_report, month_report, year_report],
                                 n_tree_per_recording=opt.n_trees,
                                 )
    else:
        generate_report_pdf_cherries(field_type, path_records, opt.path_save, path_images, n_report,
                                 date_recording=[day, month, year],
                                 date_report=[day_report, month_report, year_report],
                                 n_tree_per_recording=opt.n_trees,
                                 )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='write_pdf.py',
                                     description='This program writes a pdf journal.')

    parser.add_argument('--path-predictions', type=str, help='path to xlsx file with counts and ratios.')
    # parser.add_argument('--path-locations', default='',type=str, help='path to xlsx with locations information.')
    parser.add_argument('--path-save', type=str, help='path of file with records analysis.')
    parser.add_argument('--data-field', type=str, default='fic2-rengo-agritorre',
                        help='Names of categories in the field.')
    parser.add_argument('--day', type=int, help='day of data sample.')
    parser.add_argument('--month', type=int, help='Month of data sample.')
    parser.add_argument('--year', default=2025,type=int, help='Year of data sample.')
    parser.add_argument('--n-report',default=1, type=int, help='Report number.')
    parser.add_argument('--n-trees',default=11, type=int, help='Number of trees per recording.')
    parser.add_argument('--type-data',default="buds", choices=['buds','cherry','cherries'],
                        type=str, help='Type of data to process.')

    opt = parser.parse_args()
    main(opt)