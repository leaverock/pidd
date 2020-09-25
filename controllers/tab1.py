# -*- coding: utf-8 -*-
from .utils import my_write_merge, my_write, tab1_width, base_fmt_left, tab1_1_cols, font_size, tab1_1_header_height, \
    tab1_2_cols, tab_1_2_vert_shift, tab1_2_header_height, tab1_3_cols, tab1_3_header_height

def tab_1_1_head (workbook, worksheet, row, col, width, vert_shift, arg1, arg2, widths):
    fs = font_size
    if width == 1: fs = fs - 1

    fmt = {'valign': 'center', 'font_size': fs, 'right': 1, 'top': 1, 'text_wrap': True, }
    if arg2 == 1: fmt ['left'] = 1
    my_write_merge(workbook, worksheet, row + vert_shift, col, row + tab1_1_header_height - 1, col + width - 1, fmt, arg1)

    fmt = {'right': 1, 'top': 1, 'align': 'center'}
    if arg2 == 1: fmt ['left'] = 1
    if width > 1:
        my_write_merge(workbook, worksheet, row + tab1_1_header_height, col, row + tab1_1_header_height, col + width - 1, fmt, arg2)
    else:
        my_write(workbook, worksheet, row + tab1_1_header_height, col, fmt, arg2)

    r = col + width
    widths[int(arg2)] = [r, width]
    return r


def tab1_01_str(workbook, worksheet, row, arg):
    my_write_merge(workbook, worksheet, row + 1, 1, row + 1, tab1_width - 2, {'font_size': 14 }, arg)
    return row + 2


def table_1_1_head(workbook, worksheet, row, dbg = False):
    def q (w):
        if dbg: print ('tab1_proizv_control.tab1_table_head: col_widths: %s' % w)

    col_widths = dict.fromkeys(range(1, tab1_1_cols + 1)); q (col_widths)
    c = tab_1_1_head(workbook, worksheet, row, col=1, width=2, vert_shift=0, arg1=u'№\nп/п', arg2=1, widths=col_widths); q (col_widths)
    c = tab_1_1_head(workbook, worksheet, row, col=c, width=20, vert_shift=0, arg1=u'Наименование данных', arg2=2, widths=col_widths); q (col_widths)
    c = tab_1_1_head(workbook, worksheet, row, col=c, width=20, vert_shift=0, arg1=u'Данные', arg2=3, widths=col_widths); q (col_widths)
    summary = row + tab1_1_header_height + 1, col_widths
    if dbg: print  ('tab1_proizv_control.tab1_table_head: return: %d, %s' % (summary[0], summary[1]))
    return summary


def table_1_1_body(workbook, worksheet, row, arg, col_widths, dbg = False):
    # if dbg: rows = [0]
    # else: rows = range(len(arg)) # 0 .. 9
    rows = range(len(arg))  # 0 .. 9
    for r in rows:
        a = arg [r]
        lng_name = max(len(a[0]), len('%s' % a[1]))
        #height = int (lng_name / 35.0)
        height = int (lng_name / 65.0)
        pos, lng = col_widths[1]
        if dbg: print  ('tab1_proizv_control.table_1_1_body: height: %d, pos: %d, lng: %d' % (height, pos, lng))
        f = {'left': 1, 'right': 1, 'top': 1, 'align': 'center'}
        if r == len(rows) - 1: f ['bottom'] = 1
        my_write_merge(workbook, worksheet, row, pos - lng, row + height, pos - 1, f, r + 1)

        cols = range(1, tab1_1_cols)
        for c in cols:
            pos, lng = col_widths [c + 1]
            if dbg:
                print  ('tab1_proizv_control.table_1_1_body: c: %d, pos: %d, lng: %d, arg: %s' % ( c, pos, lng, a[c - 1]))
                print  ('tab1_proizv_control.table_1_1_body: row: %d, pos - lng: %d, row + height: %d, pos - 1: %d' % (row, pos - lng, row + height, pos - 1))
            f = {'right': 1, 'top': 1, 'text_wrap': True,}
            if r == len(arg) - 1: f ['bottom'] = 1
            my_write_merge(workbook, worksheet, row, pos - lng, row + height, pos - 1, f, a[c - 1], base_format = base_fmt_left)
        row = row + height + 1

    if dbg: print  ('tab1_proizv_control.table_1_1_body: return: %d' % (row))
    return row
