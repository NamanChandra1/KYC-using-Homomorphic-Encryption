import img2pdf
from PIL import Image
import os
import sys

def convert(img_name):
    
    pdf_path = img_name[:-4]+ ".pdf"
    # opening image
    image = Image.open(img_name)
    
    # converting into chunks using img2pdf
    pdf_bytes = img2pdf.convert(image.filename)
    
    # opening or creating pdf file
    file = open(pdf_path, "wb")
    
    # writing pdf files with chunks
    file.write(pdf_bytes)
    
    # closing image file
    image.close()
    os.remove(img_name)
    
    # closing pdf file
    file.close()
    
    # output
    print("Successfully made pdf file")