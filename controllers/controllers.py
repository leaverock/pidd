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

        # if log['controllers']:
        #     logFile ('pid.contrllers.Binary: enter cicle')
        #     for predpr in rep.v1_01:
        #         logFile ('pid.contrllers.Binary: item')

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

            def _seek_cdir(dep):
                if dep.role == 'cdir':
                    return dep
                else:
                    if dep.parent_id:
                        return _seek_cdir(dep.parent_id)
                    return dep

            if rep.postanovlenie_zakon == '1':          # КОаП РФ
                stat = u"Ст. №%d, ч. №%d, п. №%d, пп. №%d" % ( rep.postanovlenie_iskodex_1, rep.postanovlenie_iskodex_2,
                                                               rep.postanovlenie_iskodex_3, rep.postanovlenie_iskodex_4)
                if rep.protokol_iskodex_6 > 0.0:
                    nak_5 = u"административный штраф"
                else:
                    nak_5 = u"-"
                num_stat_6 = stat + '\n' + rep.protokol_description
                summa_8 = str(rep.protokol_iskodex_6) + u' руб., ' + str(rep.protokol_iskodex_7)
                summa_10 = rep.postanovlenie_iskodex_6
                numb_11 = stat
                date_12 = rep.postanovlenie_iskodex_5
                name_13 = u"Постановление о назначении административного штрафа"

            if rep.postanovlenie_zakon == '2':          # Иное законодательство
                if rep.protokol_notkodex_summa > 0.0:
                    nak_5 = u"административный штраф"
                else:
                    nak_5 = u"-"
                num_stat_6 = u"Иное законадательство" + '\n' +rep.protokol_description
                summa_8 = str(rep.protokol_notkodex_summa) + u' руб., ' + str(rep.protokol_notkodex_date)
                summa_10 = rep.postanovlenie_notkodex_summa
                numb_11 = rep.postanovlenie_notkodex_num
                date_12 = rep.postanovlenie_notkodex_date
                name_13 = rep.postanovlenie_notkodex_name

            arg = [
                [u'Принадлежность к железной дороге',  dep_id.rel_railway_id.name_get()[0][1]],
                [u'Принадлежность структурного подразделения', _seek_cdir(dep_id).name_get()[0][1]],
                [u'Подразделение на железной дороге', dep_id.name_get()[0][1]],
                [u'Надзорный орган', _v1_08_SELECTION_DICT[rep.v1_08]],
                [u'Административное наказание', nak_5],                                                 # 5 строка
                [u'Номер статьи административного правонарушения', num_stat_6],                         # 6 строка
                [u'Регламентация (содержание нарушения)', rep.act_problematica.name_get()[0][1]],       # 7 строка
                [u'Сумма предъявленного штрафа, руб.', summa_8],                                        # 8 строка
                [u'Текущее состояние ведения претензионной работы', rep.get_pret_state()],              # 9 строка
                [u'Фактически оплаченная сумма, руб.', summa_10],                                       # 10 строка
                [u'№ документа', numb_11],                                                              # 11 строка
                [u'Дата документа', date_12],                                                           # 12 строка
                [u'Наименование документа', name_13],                                                   # 13 строка
                [u'Постановляющая часть', rep.postanovlenie_description],                               # 14 строка
                [u'№, дата ЕАСД', rep.postanovlenie_num_easd + ', ' + rep.postanovlenie_date_easd],     # 15 строка
            ]
            r = table_1_1_body(workbook, worksheet, r, arg, col_widths)

        tab1(workbook, rep)

        workbook.close()
        doc_bytes.seek(0)

        return request.make_response(doc_bytes.read(),
                                     [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                      ('Content-Disposition', content_disposition(filename))])




