

import pymupdf as fitz
import pymupdf4llm
import regex as re
from typing import Sequence

#################################### TABLE EXTRACTION HELPERS (LOWER LEVEL) ####################################

def extract_cells_with_fonts_from_rect(page, rect):
    if not isinstance(rect[0], Sequence):
        # Define the bounding box (Rect)
        bounding_box = fitz.Rect(rect)

        # Extract text blocks within the bounding box
        text_blocks = page.get_text("dict", clip=bounding_box, sort=True)["blocks"]

        # Initialize a list to store cells
        cells = []

        # Filter text blocks that fall within the bounding box and include font details
        for block in text_blocks:
            for line in block["lines"]:
                for span in line["spans"]:
                    span_rect = fitz.Rect(span["bbox"])
                    if span_rect.intersects(bounding_box):
                        cells.append({
                            "type": "text",
                            "bbox": span_rect,
                            "mid_point": [(span_rect[0] + span_rect[-2]) / 2, (span_rect[1] + span_rect[-1]) / 2],
                            "content": span["text"],
                            "font": {
                                "name": span["font"],
                                "size": span["size"]
                            }
                        })
        return cells
    else:
        return [extract_cells_with_fonts_from_rect(page, r)[0] for r in rect if r]


def extract_cells_from_rect(page, rect):
    # Define the bounding box (Rect)
    bounding_box = fitz.Rect(rect)

    # Extract text blocks within the bounding box
    text_blocks = page.get_text("blocks", clip=bounding_box)

    # Initialize a list to store cells
    cells = []

    # Filter text blocks that fall within the bounding box
    for block in text_blocks:
        block_rect = fitz.Rect(block[:4])
        if block_rect.intersects(bounding_box):
            cells.append({
                "type": "text",
                "bbox": block_rect,
                "content": block[4]
            })
    return cells


def path_to_pg_sec(path, type_='path'):
    if type_ == 'stream':
        tab_str = pymupdf4llm.to_markdown(fitz.open(stream=path), margins=(0, 0))
    else:
        tab_str = pymupdf4llm.to_markdown(path, margins=(0, 0))
    doc_lst = re.split(r'\n?\[TAB\]\n', tab_str)
    page = 0
    pg_sec = []
    for i in doc_lst:
        if '\n-----\n' in i:
            page += 1
            continue
        elif i and re.match(r'[^\n]+', i):
            pg_sec.append([page, i])
    return pg_sec

#################################### TABLE EXTRACTION HELPERS (HIGH LEVEL - MARKDOWN BASED) ####################################

def tab2json(tab: Sequence[Sequence]):
    from itertools import repeat
    header = tab[0]
    rows = tab[1:]
    if rows:
        return [dict(zip(header, values)) for header, values in zip(repeat(header, len(rows)), rows)]
    else:
        return [dict((head, '') for head in header)]


def json2tab(json_):
    if not json_:
        return None
    headers = [key for key in json_[0].keys() if key != 'inner']
    rows = [[j[head] for head in headers] for j in json_]
    rows.insert(0, headers)
    return rows


def get_coords_tabstr(docsec):
    tab_coords = re.findall(r'\#{2}([\d\.\;]+)\#{2}', docsec)
    tab_coords = [float(i) for i in tab_coords[0].split(';')]
    return tab_coords, "".join(re.split(r'\#{2}.+\#{2}\n', docsec)[1:])


def outer_row_from_rect(region, page):
    return [cell['content'].strip().split('\n') for cell in extract_cells_from_rect(page, rect=fitz.Rect(region))]


def get_nested_table(finder_coords, page):
    outer_table = page.find_tables(clip=finder_coords)
    if list(outer_table):
        outer_table = outer_table[0]
        outer_coords = [finder_coords[0], outer_table.header.bbox[-1], finder_coords[2], finder_coords[3]]
        inner_tables = list(page.find_tables(clip=outer_coords, horizontal_strategy='lines_strict', intersection_x_tolerance=None))
        if inner_tables:
            if len(inner_tables) == 1 and inner_tables[0].col_count == outer_table.col_count:
                return None
            return finder_coords, [fitz.Rect(i.bbox) for i in inner_tables]
    return None

#################################### TABLE EXTRACTION ####################################

def get_header_val_table(tab):
    return {'items': [{key: val for i in range(0, len(tab) - 1, 2) for key, val in zip(tab[i], tab[i + 1]) if key}]}

def nested_table_extract(finder_coords, inner_tables, page):
    dict_ = dict()
    x1, y1, x2, y2 = finder_coords
    all_sections = []
    all_y = [y1, y2]
    [all_y.extend([y1, y2]) for x1, y1, x2, y2 in inner_tables]
    all_y = sorted(set(all_y))

    for i in range(len(all_y) - 1):
        y1, y2 = all_y[i:i + 2]
        all_sections.append([x1, y1, x2, y2])
    outer_tab_rows = outer_row_from_rect(all_sections[0], page)
    inner_tabs = []

    for i in range(1, len(all_sections)):
        table = page.find_tables(clip=all_sections[i], intersection_x_tolerance=None)
        if not list(table):
            outer_tab_rows.extend(outer_row_from_rect(all_sections[i], page))
        elif not all([table[0].header.names]) == True:
            outer_tab_rows.extend(outer_row_from_rect(all_sections[i], page))
        else:
            for tab in table:
                inner_tabs.append(tab.extract())
    if len(outer_tab_rows[-1]) != len(outer_tab_rows[0]):
        outer_tab_rows.pop(-1)
    dict_ = tab2json(outer_tab_rows)
    for row, tab in zip(dict_, inner_tabs):
        row['inner'] = tab2json(tab)
    return {'items': dict_}

######################################## IN CASE TABLE PARSER ERRORS ##################################

def nested_table_extract_1(tab):
    dict_ = dict()
    tab_rows = [i.split('|') for i in tab[1:-2].split('|\n|')]
    outer_len = len(tab_rows[0])
    outer_tab_rows = []
    inner_tabs = []
    for idx, i in enumerate(tab_rows):
        if len(i) == outer_len:
            outer_tab_rows.append(i)
            if not inner_tabs:
                inner_tabs.append([])
            elif inner_tabs[-1]:
                inner_tabs.append([])
        else:
            if not i[0]:
                i.pop(0)
            inner_tabs[-1].append(i)
    if (inner_tabs and len(outer_tab_rows[1:]) < len(inner_tabs)) or len(outer_tab_rows) == 1:
        outer_tab_rows.insert(1, ['' for i in range(len(outer_tab_rows[0]))])
    dict_ = tab2json(outer_tab_rows)
    for row, tab in zip(dict_, inner_tabs):
        row['inner'] = tab2json(tab)
    return {'items': dict_}

####################################

def get_metaH_table(tab_rows):
    dict_ = dict()
    meta_row = []
    while len(tab_rows) >= 2 and len(tab_rows[0]) != len(tab_rows[1]):
        popped_row = tab_rows.pop(0)
        meta_row.extend([i for i in popped_row if i])
    while len(tab_rows[-1]) != len(tab_rows[0]):
        popped_row = [i for i in tab_rows.pop(-1) if i]
        for i in range(len(popped_row)):
            elem = popped_row[i]
            if ':' in elem:
                #print(elem)
                if len(re.split(r'\;|\n', elem)) < 2:
                    key, value = elem.split(':')
                    dict_['_'.join([i.lower() for i in key.split()])] = value.strip() if re.match(r'\d?\.?\d+', value) else value
                else:
                    lines = re.split(r'\;|\n', elem)
                    last_key = 0
                    for i in lines:
                        if ':' in i:
                            key, value = i.split(':')
                            last_key = '_'.join([i.lower() for i in key.split()])
                            dict_[last_key] = value
                        else:
                            dict_[last_key] += value
            elif len(popped_row) == 2 and i == 0:
                dict_[elem.strip()] = re.findall(r'\d+\.?\d+', popped_row[i + 1])[0] if re.match(r'\d+\.?\d+', popped_row[i + 1]) else (popped_row[i + 1]).strip()
    dict_['items'] = tab2json(tab_rows)
    dict_['meta_headers'] = ';'.join(meta_row)
    return dict_

def extract_text(text):
    result = re.split(r'(\*{2}[^0-9\n]+\*{2}\n|\# [^0-9\n]+\n)', text)

    # Combining each header with its corresponding content
    output = [(result[i] + result[i + 1]).strip() for i in range(1, len(result) - 1, 2)]
    dict_ = dict()
    for text in output:
        if text.startswith('**'):
            t_lines = text.split('\n')
            t_lines[0] = t_lines[0].replace('**', '')
            if len(t_lines[1:]) == 2 and not t_lines[1:][0]:
                dict_[t_lines[0].lower().replace(' ', '_')] = t_lines[1:][1]
            else:
                dict_[t_lines[0].lower().replace(' ', '_')] = t_lines[1:]
        elif text.startswith('# '):
            t_lines = text.split('\n\n')
            t_lines[0] = t_lines[0].replace('# ', '')
            if len(t_lines[1:]) > 0:
                for i in t_lines[1:]:
                    if re.match(r'.*\d+.*', i) and '/' not in i:
                        dict_['reference_id'] = i.lower().strip()
                dict_['header_items'] = t_lines[1:]
            dict_['header'] = t_lines[0]
        else:
            t_lines = text.split('\n')
            dict_['misc'] = dict_.get('misc', []).extend(t_lines)
    return ['text', dict_]

def extract_table(docsec, page):
    finder_coords, tab_ = get_coords_tabstr(docsec)
    tab = [i[1:-1].split('|') for i in tab_.strip().split('\n')]
    if all([len(tab[i]) == len(tab[i + 1]) for i in range(0, len(tab) - 1, 2)]) and all([len(tab[0]) == len(tab[i]) for i in range(len(tab))]) == False and 'Total' not in tab[-1]:
        dict_ = get_header_val_table(tab)
        return 'header_val', dict_
    elif get_nested_table(finder_coords, page) != None:
        try:
            outer, inner = get_nested_table(finder_coords, page)
            dict_ = nested_table_extract(outer, inner, page)
            return ['nested', dict_]
        except:
            dict_ = nested_table_extract_1(tab_)
            return ['nested', dict_]
    else:
        dict_ = get_metaH_table(tab)
        return ['meta_header', dict_]

#################################### PAGE TRAVERSAL ####################################

def traverse_page_from_last_tab(tab_list, pres_tab):
    pres_type, dict_ = pres_tab
    header = [i for i in dict_['items'][0].keys() if i != 'inner']
    type_, last_table = tab_list[-1]
    if all([h in last_table['items'][-1].keys() for h in header]):
        if type_ == pres_type == 'nested':
            if all([dict_['items'][0][h] == '' for h in header]):
                last_table_inners = json2tab(last_table['items'][-1]['inner']) if 'inner' in last_table['items'][-1] else None
                new_table_inners = json2tab(dict_['items'][0]['inner'])
                if not last_table_inners:
                    inner_heads = [i for i in last_table['items'][0]['inner'].keys()]
                    new_table_inners.insert(0, inner_heads)
                    tab_list[-1][1]['items'][-1]['inner'] = tab2json(new_table_inners)
                elif len(last_table_inners) == 2 and all([i == '' for i in last_table_inners[-1]]):
                    new_table_inners.insert(0, last_table_inners[0])
                    tab_list[-1][1]['items'][-1]['inner'] = tab2json(new_table_inners)
                else:
                    new_table_inners.insert(0, last_table_inners[0])
                    tab_list[-1][1]['items'][-1]['inner'].extend(tab2json(new_table_inners))
                tab_list[-1][1]['items'].extend(dict_['items'][1:])
            else:
                tab_list[-1][1]['items'].extend(dict_['items'])
        elif type_ == pres_type == 'meta_header':
            last_table['items'].extend(dict_['items'])
            for key in dict_.keys():
                if key != 'items':
                    last_table[key] = dict_[key]
            if dict_.get('meta_headers', None):
                last_table['meta_headers'] = ';'.join([i for i in [last_table.get('meta_headers', ''), dict_['meta_headers']] if i])
        else:
            tab_list.append(pres_tab)
    else:
        tab_list.append(pres_tab)
    return tab_list

######################################POST_PROCESS#####################################

def key_header_post_process(item):
    from datetime import datetime
    if isinstance(item, str):
        if re.match(r'\d+\/\d+\/\d{4}', item.strip()):
            item = datetime.strptime(re.findall(r'\d+\/\d+\/\d{4}', item)[0], '%m/%d/%Y')
            return item.date()
        elif re.match(r'\$?\d+\.?\d?', item.strip()) and not re.match(r'.?[^a-zA-Z]+.?', item.strip()):
            num_pat = re.findall(r'\d+\.?\d?', item)[0]
            item = int(num_pat) if '.' not in num_pat else float(num_pat)
            return item
        else:
            return item
    elif isinstance(item, list):
        for i in range(len(item)):
            item[i] = key_header_post_process(item[i])
        return item
    elif isinstance(item, dict):
        for key in item:
            item[key] = key_header_post_process(item[key])
        return item
    return item

def get_key_header(item):
    main_list = []
    if isinstance(item, dict):
        for key in item:
            main_list.extend(get_key_header(key))
            main_list.extend(get_key_header(item[key]))
    elif isinstance(item, str):
        main_list.append(item)
    elif isinstance(item, list):
        for i in range(len(item)):
            main_list.extend(get_key_header(item[i]))
    else:
        main_list.append(str(item))
    return main_list

def extract_headers(dict_):
    main_list = []
    for key in dict_:
        if key == 'items':
            main_list.extend(extract_headers(dict_['items'][0]))
        elif key == 'inner':
            main_list.extend(extract_headers(dict_['inner'][0]))
        else:
            main_list.append(key)
    return main_list
