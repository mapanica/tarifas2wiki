#!/usr/bin/env python
# coding=utf-8

import os, sys
from PyPDF2 import PdfFileReader

# 0 = express, 1 = ruteado, 2 = interlocal
data = { 0: {}, 1: {}, 2: {} }

def main(argv):
    process_pdf('data/Resolucion Tarifas Abril 2017.pdf')
    output = generate_wiki()
    print(output)
    exit()

def get_pdf_content_lines(pdf_file_path):
    with open(pdf_file_path, 'rb') as f:
        pdf_reader = PdfFileReader(f)
        for num, page in enumerate(pdf_reader.pages):
            try:
                for idx, line in enumerate(page.extractText().splitlines()):
                    yield (idx, line)
            except KeyError:
                return

def process_pdf(input_data):
    global data

    for idx, line in get_pdf_content_lines(input_data):
        process_line(idx, line)


# 0 = from, 1 = to, 2 = price
n = -1
skip = 0
departamento = ''
# 0 = express, 1 = ruteado, 2 = interlocal
service_type = -1
origen = ''
destino = ''

def process_line(idx, line):
    global departamento, service_type, origen, destino, n, skip
    
    #skip first two lines
    if line.startswith('ORIGEN') \
    or line.startswith('DESTINO'):
        return
    
    #skip first header row
    if line.startswith('MINISTERIO DE TRANSPORTE E INFRAESTRUCTURA'):
        skip = 5
        return
    
    #skip last line
    elif line.startswith('Ultima línea'):
        skip = 2
        
    #skip last lines
    elif line.startswith('RUTAS'):
        skip = 11
        
    #skip number of lines
    elif skip > 0:
        skip = skip - 1
        return
    
    #check for new department
    elif line.startswith('DEPARTAMENTO DE '):
        departamento = line.replace('DEPARTAMENTO DE ', '').title().replace(':','')
        n = 0
    #exception: RACCN
    elif line.startswith('REGION AUTONOMA COSTA CARIBE NORTE'):
        departamento = line.title()
        n = 0
        
    #service_type
    elif line.startswith('I.- AUTOBUSES EXPRESOS'):
        service_type = 0
    elif line.startswith('II.- AUTOBUSES ORDINARIOS') \
    or line.startswith('I.- AUTOBUSES ORDINARIOS') \
    or line.startswith('II. AUTOBUSES ORDINARIOS'):
        service_type = 1
    elif line.startswith('III.- MICROBUSES INTERLOCALES') \
    or line.startswith('II.- MICROBUSES EXPRESOS') \
    or line.startswith('IV.- MICROBUSES INTERLOCALES') \
    or line.startswith('III.- MICROBUSES EXPRESOS'):
        service_type = 2
    
    #from
    elif n is 0:
        origen = line.strip()
        n = n+1
        
        #exceptions!!!!
        if origen.startswith('TICUANTEPE ('):
            origen = origen + 'de Chinandega)'
            skip = 2
        elif origen is '':
            n = n-1
        
    #to
    elif n is 1:
        destino = line.strip().replace('(Interlocal)','') #TODO: add more
        n = n+1
    
    #prize => ignore and print out
    elif n is 2:
        if departamento not in data[service_type]:
            data[service_type][departamento] = []
        data[service_type][departamento].append({'from': origen.title(), 'to': destino.title()})
        n = 0
    
    else:
        exit()

def generate_wiki():
    global data
    
    output = ''

    for (key, departamentos) in data.items():
        if key == 0: 
            output += '=Expresos=\n'
        elif key == 1: 
            output += '=Ruteados=\n'
        elif key == 2: 
            output += '=Interlocales=\n'

        output += '\n'
        output += '[Insertar introducción]\n'
        output += '\n'
                
        for departamento in sorted(list(departamentos.keys())):
            
            rutas = departamentos[departamento]
            
            output += '=='+departamento+'==\n'
            output += '\n'
            output += "Hay '''"+str(len(rutas))+" rutas''' de servicio "
            if key == 0: 
                output += 'expreso'
            elif key == 1: 
                output += 'ordinario'
            elif key == 2: 
                output += 'interlocal'
            output += " de las cuales '''0 rutas''' ya existen en OpenStreetMap.\n"
            output += '\n'
            output += '{| class="wikitable sortable"\n'
            output += '!scope="col"| Inicia en...\n'
            output += '!scope="col"| Termina en...\n'
            output += '!scope="col" class="unsortable" width="50"| Estado\n'
            output += '!scope="col" class="unsortable"| Traza(s)\n'
            output += '!scope="col" class="unsortable"| Relación\n'
            output += '!scope="col" class="unsortable"| Itinerarios\n'
            output += '!scope="col" class="unsortable"| Duración\n'
            output += '!scope="col" class="unsortable"| Notas\n'
            
            for ruta in rutas:
                output += '|-\n'
                output += '| '+ruta['from']+'\n'
                output += '| '+ruta['to']+'\n'
                output += '| {{State Transport|bu=0|ha=0|re=0}}\n'
                output += '| -\n'
                output += '| -\n'
                output += '|\n'
                output += '* -\n'
                output += '* -\n'
                output += '| ?\n'
                output += '|\n'
                
            output += '|}\n'
            output += '\n'
            
    
    return output


if __name__ == "__main__":
    main(sys.argv[1:])
