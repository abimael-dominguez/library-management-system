import csv
import datetime

def to_snake_case(s):
    return s.lower().replace(' ', '_').replace('.', '')

column_mapping = {
    'nombre': 'title',
    'autor': 'author',
    'pz': 'total_copies',
    'paginas': 'pages',
    'semanas_aut': 'max_loan_weeks',
    'estatus': 'status',
    'encargado': 'employee',
    'congregante': 'member',
    'fecha_de_prestamo': 'loan_date',
    'fecha_estimada_de_entrega': 'due_date',
    'fecha_r_de_entrega': 'actual_return_date'
}

# Columns to apply title case: title (0), author (1), status (5), employee (6), member (7)
title_columns = [0, 1, 5, 6, 7]

# Date columns: loan_date (8), due_date (9), actual_return_date (10)
date_columns = [8, 9, 10]

with open('/home/abimael/Documents/projects/library-management-system/data/raw/library-cbg.tsv', 'r', encoding='utf-8') as infile, \
     open('/home/abimael/Documents/projects/library-management-system/library-cbg-clean.csv', 'w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile, delimiter=',', quoting=csv.QUOTE_ALL)
    
    is_header = True
    for row in reader:
        if is_header:
            row = [column_mapping.get(to_snake_case(cell.strip()), to_snake_case(cell.strip())) for cell in row]
            is_header = False
        else:
            cleaned_row = []
            for i, cell in enumerate(row):
                cell = cell.strip()
                if i in title_columns:
                    cell = cell.title()
                elif i in date_columns and cell:
                    try:
                        d = datetime.datetime.strptime(cell, '%d/%m/%Y')
                        cell = d.strftime('%Y-%m-%d')
                    except ValueError:
                        pass  # leave as is if invalid
                cleaned_row.append(cell)
            row = cleaned_row
        writer.writerow(row)