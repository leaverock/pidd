# -*- coding: utf-8 -*-

###########################################################################################
#
#   general constants
#
###########################################################################################
# общие постоянные
default_cell_width = 8.43 # chars
default_cell_heigth = 15.0
my_cell_width = default_cell_width / 4.0
cell_width = default_cell_width / 4.0
font_size = 9

# вкладка 1
tab1_width = 45                     # my_cells_width_calc = 45
my_cells_width_calc = 45
tab1_1_cols = 3                     # calc_susha_table_head_cols = 25
tab1_1_header_height = 4            # calc_susha_header_height = 12
tab1_2_cols = 5
tab_1_2_vert_shift = 3              # calc_vozd_vert_shift = 3
tab1_2_header_height = 5
tab1_3_cols = 4
tab1_3_header_height = 4

base_fmt_left = {
            'text_wrap': False,
             'align': 'left',
             'valign': 'vcenter',
             'left': 0, 'right': 0, 'top': 0, 'bottom': 0,
             'font_name': 'Arial',
             'font_size': font_size,
             }

base_fmt_center = { 'text_wrap': False,
             'align': 'center',
             'valign': 'vcenter',
             'left': 0, 'right': 0, 'top': 0, 'bottom': 0,
             'font_name': 'Arial',
             'font_size': font_size,
             }

base_fmt_right = { 'text_wrap': False,
             'align': 'right',
             'valign': 'vcenter',
             'left': 0, 'right': 0, 'top': 0, 'bottom': 0,
             'font_name': 'Arial',
             'font_size': font_size,
             }

###########################################################################################
#
#   general functions
#
###########################################################################################
def add_to_format(existing_format, dict_of_properties, workbook):
    #https://stackoverflow.com/questions/21599809/python-xlsxwriter-set-border-around-multiple-cells
    """Give a format you want to extend and a dict of the properties you want to
    extend it with, and you get them returned in a single format"""

    new_dict = {}
    for key, value in existing_format.__dict__.items():
        if (value != 0) and (value != {}) and (value != None):
            new_dict[key] = value
    del new_dict['escapes']

    return(workbook.add_format(dict(new_dict.items() + dict_of_properties.items())))


def my_write(workbook, worksheet, row, col, add_fmt, body, vert = default_cell_heigth, base_format = base_fmt_left):
    fmt = workbook.add_format(base_format)
    fmt = add_to_format (fmt, add_fmt, workbook)
    worksheet.set_row(row, vert)
    worksheet.write(row, col, body, fmt)


def my_write_merge(workbook, worksheet, row0, col0, row1, col1, add_fmt, body, base_format = base_fmt_center):
    fmt = workbook.add_format(base_format)
    fmt = add_to_format (fmt, add_fmt, workbook)
    if col1 > col0:
        worksheet.merge_range(row0, col0, row1, col1, body, fmt)
    else: # col1 == col0
        if row0 == row1:
            worksheet.write(row0, col0, body, fmt)


