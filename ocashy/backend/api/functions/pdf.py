import os
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A5
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
import datetime


def create_pdf(bayar,data_list,tipe):
    total_harga = sum(item['Price'] for item in data_list)
    kembalian = bayar - total_harga
    sample_style_sheet = getSampleStyleSheet()
    sample_style_sheet['Italic'].fontSize = 6
    sample_style_sheet['Italic'].leading = 2
    sample_style_sheet['Heading1'].leading = 6
    sample_style_sheet['BodyText'].leading = 6
    sample_style_sheet['Heading1'].fontSize = 10
    sample_style_sheet['BodyText'].fontSize = 7
    
    # Get current date and time
    now = datetime.datetime.now()
    fktrname = now.strftime("%d-%m-%Y-%H,%M,%S")
    waktu = now.strftime('%d-%m-%Y:%H-%M-%S')
    filename = now.strftime("%d-%m-%Y-%H,%M,%S") + ".pdf"

    pdf = SimpleDocTemplate('../../../ocashy/receipts/'+filename, pagesize=landscape(A5), topMargin = 5, leftMargin = 10, rightMargin = 10, bottomMargin = 0)
    elements = []


    # Define table header
    table_header = ['No','Produk', 'Kuantitas', 'Diskon', 'Harga Diskon', 'Gudang', 'Harga']

    # Split data into chunks of 10
    # chunks = [data_list[i:i + 8] for i in range(0, len(data_list), 8)]
    chunks = [data_list[:7]]  # First chunk of 8 items
    chunks += [data_list[i:i + 9] for i in range(7, len(data_list), 10)]  # Subsequent chunks of 10 items



    total_items = 0  # Keep track of total items processed
    paragraph_0 = Paragraph(f"Nota Penjualan {tipe}", sample_style_sheet['BodyText'])
    paragraph_1 = Paragraph("Istana Keramik", sample_style_sheet['Heading1'])
    paragraph_2 = Paragraph("Jl. WR Supratman No.24, Baledono, Kec. Purworejo, Kabupaten Purworejo, Jawa Tengah 54118", sample_style_sheet['BodyText'])
    paragraph_3 = Paragraph("Telp   :   (0275) 321 597 | WhatsApp   :   087714141252", sample_style_sheet['BodyText'])
    paragraph_4 = Paragraph("Website    :   https://istanakeramik.com", sample_style_sheet['BodyText'])
    paragraph_6 = Paragraph(f"Nomor Faktur : {fktrname}     Waktu :    {waktu}", sample_style_sheet['BodyText'])
    paragraph_footer = Paragraph("*Mohon barang di periksa dulu sebelum meninggalkan toko.",sample_style_sheet['Italic'])
    paragraph_footer2 = Paragraph("**Barang yang sudah dibeli tidak dapat ditukar kembali",sample_style_sheet['Italic'])
    catatan =  Paragraph("CATATAN TAMBAHAN :",sample_style_sheet['Italic'])
    
    elements.append(paragraph_0) 
    elements.append(paragraph_1)
    elements.append(paragraph_2)
    elements.append(paragraph_3)
    elements.append(paragraph_4)
    elements.append(paragraph_6)
    elements.append(Spacer(0, 20))
    
    char_limit = 40
    
    for chunk_index, chunk in enumerate(chunks):
    # Convert dictionaries to lists, add numbering and table header
        data = [table_header]
        for i, item in enumerate(chunk):
            item_values = list(item.values())
        
        # Check if product name exceeds the character limit
            if len(item_values[0]) > char_limit:
                # Split the product name
                item_values[0] = item_values[0][:char_limit] + '\n' + item_values[0][char_limit:]
            data.append([total_items + i + 1] + item_values)
        total_items += len(chunk)  # Update total items processed
        if chunk_index == len(chunks) - 1:
            data.append(['', '', '', '', '', 'Total', total_harga])
            data.append(['', '', '', '', '', 'Bayar', bayar])
            data.append(['', '', '', '', '', 'Kembalian', kembalian])
        

        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPMARGIN', (0, 0), (-1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(table)

        

        if chunk_index < len(chunks) - 1:            
            elements.append(PageBreak())

        if chunk_index == len(chunks) - 1:
            elements.append(paragraph_footer)
            elements.append(paragraph_footer2)
            elements.append(catatan)
        
    pdf.build(elements)
    add_watermark_to_pdf('../../../ocashy/receipts/'+filename, '../../../ocashy/test.png')
    return {"response":f"http://localhost:8000/pdfs/{filename}"}





def add_watermark_to_pdf(pdf_file_path, watermark_image_path):
    """
    Adds a watermark image to the center of every page of a PDF file and overwrites the original file.

    Args:
        pdf_file_path (str): Path to the input PDF file.
        watermark_image_path (str): Path to the watermark image.

    Returns:
        None
    """
    pdf_reader = PdfReader(open(pdf_file_path, "rb"))
    pdf_writer = PdfWriter()

    # Get the dimensions of the watermark image
    watermark_img = ImageReader(watermark_image_path)
    watermark_width = float(watermark_img.getSize()[0])
    watermark_height = float(watermark_img.getSize()[1])

    # Add watermark to each page
    for page_num in range(len(pdf_reader.pages)):
        pdf_page = pdf_reader.pages[page_num]
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Calculate the position to center the watermark
        page_width = float(pdf_page.mediabox[2])
        page_height = float(pdf_page.mediabox[3])
        x_position = (page_width - watermark_width) / 2
        y_position = (page_height - watermark_height) / 2
        
        can.drawImage(watermark_image_path, x_position, y_position, mask='auto')  # Center the image
        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        pdf_page.merge_page(new_pdf.pages[0])
        pdf_writer.add_page(pdf_page)

    # Save the modified PDF to overwrite the original file
    with open(pdf_file_path, "wb") as output_file:
        pdf_writer.write(output_file)



# Example usage:
#data_list = [{'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 10000},
#             {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
#             {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
#             {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
#             {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
#             {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
#            {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
#             {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
#             {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
 #            {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
   #          {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
 #            {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 100000000},
  #           {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 10000},
     #        {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 10000},
    #         {'Product': 'Kran BCP FLEXIBLE SILFRA WL-02 1/2 A26 COMU2/MA', 'Quantity': 10, 'Discount': '5', 'Discounted Amount': 50, 'Warehouse': 'Warehouse1', 'Price': 10000},]

#create_pdf(data_list)

        