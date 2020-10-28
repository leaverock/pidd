# -*- coding: utf-8 -*-
from math import ceil

from .utils import my_write_merge, my_write, tab1_width, base_fmt_left, tab1_cols, font_size, tab1_header_height, \
    tab1_2_cols, tab_1_2_vert_shift, tab1_2_header_height, tab1_3_cols, tab1_3_header_height
from ..util import logFile, log, logInfo


def tab1_str(workbook, worksheet, row, arg):
    my_write_merge(workbook, worksheet, row + 1, 1, row + 1, tab1_width - 2, {'font_size': 14 }, arg)
    return row + 2


def tab_1_head(workbook, worksheet, row, col, width, arg1, arg2, widths):
    fmt = {'valign': 'center', 'font_size': font_size, 'right': 1, 'top': 1, 'text_wrap': True, }
    if arg2 == 1: fmt['left'] = 1
    my_write_merge(workbook, worksheet, row, col, row + tab1_header_height - 1, col + width - 1, fmt,
                   arg1)

    r = col + width
    widths[int(arg2)] = [r, width]
    return r


def table_1_head(workbook, worksheet, row, dbg = False):
    col_widths = dict.fromkeys(range(1, tab1_cols + 1))
    c = tab_1_head(workbook, worksheet, row, col=1, width=5, arg1=u'Принад-лежность к железной дороге', arg2=1, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=5, arg1=u'Принад-лежность структурного подразделения', arg2=2, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=5, arg1=u'Подразделение на железной дороге', arg2=3, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=4, arg1=u'Надзорный орган', arg2=4, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=4, arg1=u'Администра-тивное наказание', arg2=5, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=4, arg1=u'Номер статьи администра-тивного право-нарушения', arg2=6, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=10, arg1=u'Регламентация (содержание нарушения)', arg2=7, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=4, arg1=u'Сумма предъяв-ленного штрафа, тыс.руб.', arg2=8, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=5, arg1=u'Текущее состояние ведения претензионной работы', arg2=9, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=4, arg1=u'Фактически оплаченная сумма, тыс.руб.', arg2=10, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=5, arg1=u'№ документа', arg2=11, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=5, arg1=u'Дата документа', arg2=12, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=5, arg1=u'Наименование документа', arg2=13, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=5, arg1=u'Постанов-ляющая часть', arg2=14, widths=col_widths)
    c = tab_1_head(workbook, worksheet, row, col=c, width=4, arg1=u'№, дата ЕАСД', arg2=15, widths=col_widths)

    summary = row + tab1_header_height, col_widths
    if dbg: logInfo  ('tab_single.table_1_head: return: %d, %s' % (summary[0], summary[1]))
    return summary


def table_1_body(workbook, worksheet, row, arg, col_widths):

    def h(pos, arg, filling):
        l = len(arg)
        _, lng = col_widths[pos + 1]
        r = int (ceil (float(l) / float(lng)) * filling)

        if log['controllers']:
            logInfo('pid.controllers.tab_single.table_1_body.h: pos: %d, arg: "%s"' % (pos, arg))
            logInfo('pid.controllers.tab_single.table_1_body.h: len(arg): %d, col_widths[pos + 1]: %d, height: %d' % (l, lng, r))

        return r

    rows = range(len(arg))
    for r in rows:
        a = arg [r]
        height = max(h(i, x, .4) for i, x in enumerate(a))
        if log['controllers']:
            logInfo('pid.controllers.tab_single.table_1_body: height: %d' % (height))

        cols = range(1, tab1_cols + 1)
        for c in cols:
            pos, lng = col_widths[c]
            f = {'right': 1, 'top': 1, 'text_wrap': True,}
            if c == 1: f ['left'] = 1
            if r == len(arg) - 1: f ['bottom'] = 1
            my_write_merge(workbook, worksheet, row, pos - lng, row + height, pos - 1, f, a[c - 1], base_format = base_fmt_left)

        row = row + height + 1

    return row