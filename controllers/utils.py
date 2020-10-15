# -*- coding: utf-8 -*-
from ..util import  log, logInfo

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

###########################################################################################
#
#   particular functions
#
###########################################################################################

def get_report_data_from_record(s):

    def get_data_from_one_dep():
        _v1_08_NADZ = [("nadz", u"Росприроднадзор")]; _v1_08_PROC = [("proc", u"Прокуратура")]
        _v1_08_SELECTION_DICT = dict(_v1_08_NADZ + _v1_08_PROC)

        def _seek_cdir(dep):
            if dep.role == 'cdir':
                return dep
            else:
                if dep.parent_id:
                    return _seek_cdir(dep.parent_id)
                return dep

        def get_val_cond(val, cond):
            r = ''
            if cond:
                try:
                    r = str(val)
                except:
                    r = unicode(val)
            return r

        def get_val(val, pref='', post=''):
            return pref + get_val_cond(val, val) + post

        if s.postanovlenie_zakon == '1':  # КОаП РФ
            stat = u"Ст. №%s, ч. №%s, п. №%s, пп. №%s" % (
                get_val(s.postanovlenie_iskodex_1), get_val(s.postanovlenie_iskodex_2),
                get_val(s.postanovlenie_iskodex_3), get_val(s.postanovlenie_iskodex_4))
            if s.protokol_iskodex_6 > 0.0:
                nak_5 = u"административный штраф"
            else:
                nak_5 = u"-"
            num_stat_6 = stat + get_val(s.protokol_description, pref=u', ')
            summa_8 = get_val(s.protokol_iskodex_6, post=u' руб.') + get_val(s.protokol_iskodex_7, pref=u', ')
            summa_10 = get_val(s.postanovlenie_iskodex_6)
            numb_11 = stat
            date_12 = get_val(s.postanovlenie_iskodex_5)
            name_13 = u"Постановление о назначении административного штрафа"

        if s.postanovlenie_zakon == '2':  # Иное законодательство
            if s.protokol_notkodex_summa > 0.0:
                nak_5 = u"административный штраф"
            else:
                nak_5 = u"-"
            num_stat_6 = u"Иное законадательство" + get_val(s.protokol_description, pref=u', ')
            summa_8 = get_val(s.protokol_notkodex_summa, post=u' руб.') + get_val(s.protokol_notkodex_date, pref=u', ')
            summa_10 = get_val(s.postanovlenie_notkodex_summa)
            numb_11 = get_val(s.postanovlenie_notkodex_num)
            date_12 = get_val(s.postanovlenie_notkodex_date)
            name_13 = get_val(s.postanovlenie_notkodex_name)

        rez = [
            get_val_cond(dep_id.rel_railway_id.name_get()[0][1], dep_id.rel_railway_id),  # 1 строка
            #_seek_cdir(dep_id).name_get()[0][1],  # 2 строка
            dep_id.name_get()[0][1],  # 3 строка
            _v1_08_SELECTION_DICT[s.v1_08],  # 4 строка
            get_val_cond(nak_5, s.protokol_file),  # 5 строка
            get_val_cond(num_stat_6, s.protokol_file),  # 6 строка
            get_val_cond(s.act_problematica.name_get()[0][1], s.act_problematica),  # 7 строка
            get_val_cond(summa_8, s.protokol_file),  # 8 строка
            s.get_pret_state(),  # 9 строка
            summa_10,  # 10 строка
            get_val_cond(numb_11, s.postanovlenie_file),  # 11 строка
            get_val_cond(date_12, s.postanovlenie_file),  # 12 строка
            get_val_cond(name_13, s.postanovlenie_file),  # 13 строка
            get_val_cond(s.postanovlenie_description, s.postanovlenie_description and s.postanovlenie_file),  # 14 строка
            get_val_cond((get_val(s.postanovlenie_num_easd) + get_val(s.postanovlenie_date_easd, pref=u', ')), s.postanovlenie_file),  # 15 строка
        ]
        return rez


    if not s.v1_01:
        raise

    r = []
    for dep_id in s.v1_01[0]:
        if log['controllers']:
            logInfo('pid.controllers.utils.get_report_data_from_record: department_id: %s' % (dep_id.department_id.name_get()[0][1]))
        r.append(get_data_from_one_dep())

    return r
