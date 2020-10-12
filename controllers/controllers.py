# -*- coding: utf-8 -*-
from openerp import http, exceptions
from openerp.addons.web.controllers.main import serialize_exception, content_disposition
from io import BytesIO
import xlsxwriter
from ..util import logFile, log, logInfo
from utils import tab1_width, cell_width
from tab1 import tab1_01_str, table_1_1_head, table_1_1_body
from ..models.models import _v1_08_SELECTION_DICT

class Binary(http.Controller):
    #/eco_pret_isk/export_pret_isk_xlsx -  from wizards
    @http.route('/eco_pret_isk/export_pret_isk_xlsx', type='http', auth="user")
    @serialize_exception
    def export_pret_isk_xlsx(self, id, filename, **kw):

        request = http.request
        rep = request.env['eco.pret_isk.export.wz'].browse([int(id)]).pret_isk_ids
        rep.ensure_one()
        doc_bytes = BytesIO()
        workbook = xlsxwriter.Workbook(doc_bytes)

        logInfo('*** pid.controllers.export_pret_isk_xlsx: rep.postanovlenie_zakon: %s' % rep.postanovlenie_zakon)

        def seek_cdir(dep):
            if dep.role == 'cdir':
                return dep
            else:
                if dep.parent_id:
                    return seek_cdir(dep.parent_id)
                return dep

        def get_val(cond, val):
            if cond:
                res = val
            else:
                res = ''
            return res
            

        def tab1(workbook, rep):
            #####################################################################################################################
            #
            #   Вкладка: Информация о предъявленных административных штрафах на юридическое лицо
            #
            #####################################################################################################################
            worksheet = workbook.add_worksheet(u'Штрафы')
            worksheet.set_column(0, tab1_width - 1, cell_width)
            r = tab1_01_str(workbook, worksheet, 0, u'Информация о предъявленных административных штрафах на юридическое лицо')
            r, col_widths = table_1_1_head(workbook, worksheet, r)
            if not rep.v1_01:
                raise
            dep_id = rep.v1_01[0]


            if rep.postanovlenie_zakon == '1':          # КОаП РФ
                stat = u"Ст. №%s, ч. №%s, п. №%s, пп. №%s" % ( get_val (rep.postanovlenie_iskodex_1, rep.postanovlenie_iskodex_1),
                                                               get_val (rep.postanovlenie_iskodex_2, rep.postanovlenie_iskodex_2),
                                                               get_val (rep.postanovlenie_iskodex_3, rep.postanovlenie_iskodex_3),
                                                               get_val (rep.postanovlenie_iskodex_4, rep.postanovlenie_iskodex_4))
                if rep.protokol_iskodex_6 > 0.0:
                    nak_5 = u"административный штраф"
                else:
                    nak_5 = u"-"
                num_stat_6 = stat + '\n' + get_val (rep.protokol_description, rep.protokol_description)
                summa_8 = get_val(rep.protokol_iskodex_6, str(rep.protokol_iskodex_6))\
                          + u' руб., ' + get_val(rep.protokol_iskodex_7, str(rep.protokol_iskodex_7))
                summa_10 = get_val(rep.postanovlenie_iskodex_6, rep.postanovlenie_iskodex_6)
                numb_11 = stat
                date_12 = get_val(rep.postanovlenie_iskodex_5, rep.postanovlenie_iskodex_5 )
                name_13 = u"Постановление о назначении административного штрафа"

            if rep.postanovlenie_zakon == '2':          # Иное законодательство
                if rep.protokol_notkodex_summa > 0.0:
                    nak_5 = u"административный штраф"
                else:
                    nak_5 = u"-"
                num_stat_6 = u"Иное законадательство" + '\n' + get_val(rep.protokol_description, rep.protokol_description)
                summa_8 =  get_val(rep.protokol_notkodex_summa, str(rep.protokol_notkodex_summa))\
                          + u' руб., ' + get_val(rep.protokol_notkodex_date, str(rep.protokol_notkodex_date) )
                summa_10 = get_val(rep.postanovlenie_notkodex_summa , rep.postanovlenie_notkodex_summa)
                numb_11 = get_val(rep.postanovlenie_notkodex_num, rep.postanovlenie_notkodex_num)
                date_12 = get_val(rep.postanovlenie_notkodex_date, rep.postanovlenie_notkodex_date)
                name_13 = get_val(rep.postanovlenie_notkodex_name, rep.postanovlenie_notkodex_name)

            logInfo('*** pid.controllers.export_pret_isk_xlsx.tab1: rep.postanovlenie_zakon: %s' % rep.postanovlenie_zakon)
            logInfo('*** pid.controllers.export_pret_isk_xlsx.tab1: stat: %s' % stat)
            logInfo('*** pid.controllers.export_pret_isk_xlsx.tab1: num_stat_6: %s' % num_stat_6)

            arg = [
                #[u'Принадлежность к железной дороге',  dep_id.rel_railway_id.name_get()[0][1] if dep_id.rel_railway_id else ''],
                [u'qqqПринадлежность к железной дороге',  get_val(dep_id.rel_railway_id, dep_id.rel_railway_id.name_get()[0][1] )],
                [u'Принадлежность структурного подразделения', seek_cdir(dep_id).name_get()[0][1]],
                [u'Подразделение на железной дороге', dep_id.name_get()[0][1]],
                [u'Надзорный орган', _v1_08_SELECTION_DICT[rep.v1_08]],
                [u'Административное наказание', get_val(rep.protokol_file, nak_5)],                                                 # 5 строка
                #[u'Номер статьи административного правонарушения', get_val(rep.protokol_file, num_stat_6)],                         # 6 строка
                [u'Номер статьи административного правонарушения',  num_stat_6],                         # 6 строка
                [u'Регламентация (содержание нарушения)', get_val (rep.act_problematica, rep.act_problematica.name_get()[0][1])],       # 7 строка
                [u'Сумма предъявленного штрафа, руб.', get_val (rep.protokol_file, summa_8)],                                        # 8 строка
                [u'Текущее состояние ведения претензионной работы', rep.get_pret_state()],              # 9 строка
                [u'Фактически оплаченная сумма, руб.', summa_10],                                       # 10 строка
                [u'№ документа', get_val (rep.postanovlenie_file, numb_11)],                                                              # 11 строка
                [u'Дата документа', get_val (rep.postanovlenie_file, date_12)],                                                           # 12 строка
                [u'Наименование документа', get_val (rep.postanovlenie_file, name_13)],                                                   # 13 строка
                [u'Постановляющая часть', get_val (rep.postanovlenie_description or rep.postanovlenie_file, rep.postanovlenie_description)],  # 14 строка                
                [u'№, дата ЕАСД', (get_val (rep.postanovlenie_num_easd, rep.postanovlenie_num_easd) + ', '
                    + get_val(rep.postanovlenie_date_easd, rep.postanovlenie_date_easd)) if rep.postanovlenie_file else ''],                 # 15 строка
            ]
            r = table_1_1_body(workbook, worksheet, r, arg, col_widths)

        tab1(workbook, rep)

        workbook.close()
        doc_bytes.seek(0)

        return request.make_response(doc_bytes.read(),
                                     [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                      ('Content-Disposition', content_disposition(filename))])


    @http.route('/pid/download_help', type='http', auth="public")
    @serialize_exception
    def pid_download_help(self):
        import os
        #help_file_name = u'Карта_сайта_и_необходимые_доработки.pdf'
        help_file_name = u'ПИД.pdf'
        with open(os.path.split(__file__)[0] + u'/' + help_file_name, 'rb') as f:
            doc_bytes = f.read()

        return http.request.make_response(doc_bytes,
                                     [('Content-Type', 'application/pdf'),
                                      ('Content-Disposition', content_disposition(help_file_name))])


    @http.route('/pid/export_multi', type='http', auth="user")
    @serialize_exception
    def pid_export_multi(self, id, filename, **kw):


        request = http.request
        wz = request.env['eco.pid.multi.wz'].search([('id', '=', id)])

        doc_bytes = BytesIO()
        workbook = xlsxwriter.Workbook(doc_bytes)


        year1 = wz.year
        year2 = wz.year
        month1 = (int(wz.quarter) - 1) * 3 + 1
        month2 = month1 + 3
        if month2 > 12:
            year2 = str(int(year1) + 1)
            month2 -= 12

        pid_ids = request.env['eco.pret_isk'].search([('create_date', '>=', "%s-%s-01" % (year1, month1)),('v1_06', '<', "%s-%s-01" % (year2, month2))])
        for rep in pid_ids:
            logInfo(pid_ids)

        workbook.close()
        doc_bytes.seek(0)

        return request.make_response(doc_bytes.read(),
                                     [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                      ('Content-Disposition', content_disposition(filename))])

