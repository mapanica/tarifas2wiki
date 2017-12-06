#!/usr/bin/env python
# coding=utf-8

import os, sys
from PyPDF2 import PdfFileReader

def main(argv):
	
    output = process_pdf('data/Resolucion Tarifas Abril 2017.pdf')

    return output

def get_pdf_content_lines(pdf_file_path):
    with open(pdf_file_path, 'rb') as f:
        pdf_reader = PdfFileReader(f)
        for num, page in enumerate(pdf_reader.pages):
            if num is 3:
                continue
            for idx, line in enumerate(page.extractText().splitlines()):
                yield (idx, line)
            if num is 12:
                exit()

def process_pdf(input_data):
    output = ''

    for idx, line in get_pdf_content_lines(input_data):
        process_line(idx, line)
        
    return output

# 0 = from, 1 = to, 2 = price
n = -1
skip = 0
departamento = ''
# 0 = express, 1 = ruteado, 2 = interlocal
service_type = -1
origen = ''
destino = ''

output = { 'express': [], 'ruteado': [], 'interlocal': [] }

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
        
    #skip number of lines
    elif skip > 0:
        skip = skip - 1
        return
    
    #check for new department
    elif line.startswith('DEPARTAMENTO DE '):
        departamento = line.replace('DEPARTAMENTO DE ', '')
        n = 0
        print('===' + departamento + '===')
        
    #service_type
    elif line.startswith('I.- AUTOBUSES EXPRESOS'):
        service_type = 0
        print ('service_type:', service_type)
    elif line.startswith('II.- AUTOBUSES ORDINARIOS') \
    or line.startswith('I.- AUTOBUSES ORDINARIOS') \
    or line.startswith('II. AUTOBUSES ORDINARIOS'):
        service_type = 1
        print ('service_type:', service_type)
    elif line.startswith('III.- MICROBUSES INTERLOCALES') \
    or line.startswith('II.- MICROBUSES EXPRESOS') \
    or line.startswith('IV.- MICROBUSES INTERLOCALES') \
    or line.startswith('III.- MICROBUSES EXPRESOS'):
        service_type = 2
        print ('service_type:', service_type)
    
    
    #from
    elif n is 0:
        origen = line.strip()
        n = n+1
        
        #exceptions!!!!
        if origen.startswith('TICUANTEPE ('):
            origen = origen + 'de Chinandega)'
            skip = 2
        
    #to
    elif n is 1:
        destino = line.strip().replace('(Interlocal)','').replace('(expreso)','') #TODO: add more
        n = n+1
    
    #prize => ignore and print out
    elif n is 2:
        print(origen, destino)
        n = 0
    
    else:
        print(idx, line)
        exit()

def generate_json(input_data, header_data):
    
    output = {}
    header_line = True
    
    # add header information
    if header_data is not None:
        header_keys = ['start_date','end_date','excluded_lines','included_lines']
        for key in header_keys:
            if key in header_data:
                output[key] = header_data[key]
            else:
                sys.stderr.write("Warning: The header json file lacks the key '%s'.\nYou HAVE TO add it later manually.\n" % key)

	# add basic json structure
    output['updated'] = datetime.date.today().isoformat()
    output['lines'] = {}

    # Loop through bus lines
    for data in input_data:

		#Ignore header line
        if header_line is True:
            header_line = False
            continue

        ref = data[CSV_IDX_REF]
        if ref not in output["lines"]:
            output["lines"][ref] = []
        fr = data[CSV_IDX_FROM]
        to = data[CSV_IDX_TO]
        
        exceptions = data[CSV_IDX_EXCEPTIONS].split(";")
        if exceptions[0] == '' :
            exceptions = []
        
        # Prepare schedule
        opening_hours = data[CSV_IDX_HOURS].split(";")
        opening_services = {}

        for i, d in enumerate(opening_hours):

            # Convert into understandable service schedules
            (opening_service, opening_hour) = opening_hours[i].strip().split(' ')

            if opening_service in opening_services:
                opening_services[opening_service].append(opening_hour)
            else:
                opening_services[opening_service] = [opening_hour]
            
            
        for opening_service in opening_services.keys():
            # output timetable information
            service = {
                "from": fr,
                "to": to,
                "services": [opening_service],
                "stations": [fr, to],
                "exeptions": exceptions,
                "times": []
            }
            for opening_hour in opening_services[opening_service]:
                service["times"] += generate_times(opening_hour, int(data[CSV_IDX_DURATION]), float(data[CSV_IDX_FREQUENCY]))
            
            output["lines"][ref].append(service)
    
    return output


def generate_times(hour, duration, frequency):

    data_index = int()
    schedule = dict()
    times = list()

    regex = re.search(r"([0-9]+):([0-9]+)-([0-9]+):([0-9]+)" , hour)
    if regex is not None:
        (start_hour, start_min, end_hour, end_min) = regex.groups()
    else:
        regex = re.search(r"([0-9]+):([0-9]+)" , hour)
        if regex is None:
            sys.stderr.write("Error: Some format error in the opening_hours. Please check your frequencies.csv.\n")
            sys.exit(0)
        (start_hour, start_min) = regex.groups()
        (end_hour, end_min) = (start_hour, start_min)

    (start_hour, start_min, end_hour, end_min) = (int(start_hour), int(start_min), int(end_hour), int(end_min))

    # get number of minutes between public transport service
    if frequency == 0:
        sys.stderr.write("Error: You can not use the value '0' for frequency. Please check your frequencies.csv.\n")
        sys.exit(0)
    
    if MODE_PER_HOUR:
        minutes = 60 // frequency # exception (frequency = 0) already prevented
    else:
        minutes = frequency
        
    next_min = 0
    current_hour = start_hour
    
    while current_hour <= end_hour:
        
        # first service leaves at opening_hour {start_hour}:{start_min}
        if current_hour == start_hour:
            next_min = start_min
        
        until = 59
        # in the last hour, only services until {end_hour}:{end_min}
        if current_hour == end_hour:
            until = end_min

        # calculate times for the {current_hour} until (59 or {end_min})
        while next_min <= until:
            times.append(calculate_times(current_hour, int(next_min), duration))
            next_min = next_min + minutes
        
        # prepare next_min for next hour
        if current_hour == end_hour:
            current_hour += 1
        current_hour +=  (next_min // 60)
        next_min = next_min % 60
        
    
    return times

def calculate_times(hour, start_time, duration):

    calculated_time = list()

    calculated_time.append("%02d:%02d" % (hour,start_time))

    # Calculate end_time
    end_time = start_time + duration
    
    if end_time >= 60:
        hour = hour + (end_time // 60)
        end_time = end_time % 60

    calculated_time.append("%02d:%02d" % (hour,end_time))

    return calculated_time

if __name__ == "__main__":
    main(sys.argv[1:])
