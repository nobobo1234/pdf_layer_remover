import inquirer
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import DecodedStreamObject, EncodedStreamObject, NameObject, NullObject
from os import listdir, remove
from os.path import isfile, join
import pypdftk

pdf_files = [f for f in listdir('.') if isfile(join('.', f)) and f.endswith('pdf')]
if len(pdf_files) == 0:
    print("Directory must contain pdf files.")
    exit(1)

questions = [
        inquirer.List('input',
            message="Name of the file you want to remove a layer from",
            choices=pdf_files),
        inquirer.Text('output', message="Name of output file (without .pdf)")
]

answers = inquirer.prompt(questions)

uncompressed = pypdftk.uncompress(answers['input'])

with open(uncompressed, 'rb') as data, open(f'temp_uncompressed.pdf', 'wb') as out:
    pdf = PdfFileReader(data)

    # Make an empty pdf file to write the file to.
    output = PdfFileWriter()

    page = pdf.getPage(0)
    contents = page.getContents()
    question = [inquirer.List('to_remove', message="Layer to remove", choices=list(range(1, len(contents) + 1)) + ["last layer"])]

    answer = inquirer.prompt(question)
    if answer['to_remove'] == "last layer":
        answer['to_remove'] = 0

    # Remove the same object for all the pages.
    for i in range(0, pdf.getNumPages()):
        page = pdf.getPage(i)

        # Get all the objects/layers on the page.
        contents = page.getContents()

        # Play with the number -1. -1 automatically takes the last object
        # on the pdf page but it could be another one you'd want to remove.
        streamObj = contents[int(answer['to_remove']) - 1].getObject()

        # Get the contents of the layer. This is basically pdf code that
        # describes the layer.
        data = streamObj.getData()

        # Set the data in the layer to nothing so that it dissapears.
        streamObj.setData(b'')

        # Add a copy of the page without the object/layer to the output.
        output.addPage(page)

    # Write the output to the opened output file.
    output.write(out)

pypdftk.compress('temp_uncompressed.pdf', f"{answers['output']}.pdf")
remove('temp_uncompressed.pdf')
