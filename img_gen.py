from pdf2image import convert_from_path
pages=['0']


def convert(name):
    pages.extend(convert_from_path(name,200,poppler_path= r'C:/poppler-0.68.0/bin') )
    name = name[:-4]
    doc_name = name+".jpg"
    pages[1].save(doc_name,'JPEG')
    return doc_name