# -*- coding: utf-8 -*-
from openerp import http, exceptions
from openerp.addons.web.controllers.main import serialize_exception, content_disposition
from io import BytesIO
import xlsxwriter
from ..util import log, logInfo
from utils import get_report_data_from_record

from ..models.export import MyWorkbook

class Binary(http.Controller):

    @http.route('/pid/download_help', type='http', auth="public")
    @serialize_exception
    def pid_download_help(self):
        import os
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
        for pid_no, pid in enumerate(pid_ids):
            if log['controllers']:
                logInfo('controllers.pid_export_multi: record # %d' % (pid_no))
                form_data = get_report_data_from_record(pid)
                for i, d in enumerate(form_data):
                    logInfo('controllers.pid_export_multi: form_data (%d): %s' %  (i, d))

        workbook.close()
        doc_bytes.seek(0)

        return request.make_response(doc_bytes.read(),
                                     [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                      ('Content-Disposition', content_disposition(filename))])




    @http.route('/pid/sud/export_multi', type='http', auth="user")
    @serialize_exception
    def pid_export_multi(self, id, filename, **kw):

        request = http.request
        wz = request.env['eco.pret_isk.sud.multi.wz'].search([('id', '=', id)])

        workbook = MyWorkbook()
        worksheet = workbook.add_worksheet(u'Отчёт')

        year1 = wz.year
        year2 = wz.year
        rw_id = wz.railway_id
        if wz.nakopit:
            month1 = 1
        else:
            month1 = (int(wz.quarter) - 1) * 3 + 1
        month2 = month1 + 3
        if month2 > 12:
            year2 = str(int(year1) + 1)
            month2 -= 12
        sud_ids = request.env['eco.pret_isk.sud'].search([('data_predyavlenia', '>=', "%s-%s-01" % (year1, month1)),('data_predyavlenia', '<', "%s-%s-01" % (year2, month2))])
        sud_ids_rcku = sud_ids.filtered(lambda rec: rec.department_id.role == 'rcku')
        sud_ids_filial = sud_ids - sud_ids_rcku

        grey_cell_format = {
            'border': 1,
            'align': 'center',
            'bg_color': '#D9D9D9',
        }
    
        rzd_cdir_ids = request.env['eco.department'].sudo().search([('role','=','cdir'),('parent_id.parent_id','=',False)])
        first_col = [
            (u'1. Количество предъявленных исков  к ОАО «РЖД», шт, в том числе:', grey_cell_format, row0)
            (u'1.1. Количество обжалованных исков, шт', workbook.cell_format, row1)
            (u'1.2. Количество отмененных исков, шт', workbook.cell_format, row2)
            (u'1.3. Количество исков, возмещенных ОАО "РЖД", шт', workbook.cell_format, row3)
            (u'2. Сумма предъявленных исков, тыс.руб.:', grey_cell_format, row4)
            (u'2.1. Сумма обжалованных исков, тыс.руб. ', workbook.cell_format, row5)
            (u'2.2. Сумма отмененных исков, тыс. руб.', workbook.cell_format, row6)
            (u'2.3. Сумма исков, возмещенных ОАО "РЖД", тыс. руб.', workbook.cell_format, row7)
            (u'3. Количество судебных решений по искам к ОАО "РЖД", шт', workbook.cell_format, row8)
            (u'4.Выплачено в целях удовлетворения исковых требований за вред, причиненный в результате нарушения законодательства в области охраны окружающей среды и санитарно-эпидемиологического благополучия населения, всего, тыс. руб.:', grey_cell_format, row9)
            (u'4.1. В виде денежной компенсации вреда окружающей среде, причиненного нарушением законодательства в области охраны окружающей среды, тыс. руб. ', grey_cell_format, row10)
            (u'4.2. В виде денежной компенсации вреда  вследствие нарушения санитарного законодательств, тыс. руб. ', workbook.cell_format, row11)
        ]
        def counter_factory(start=0):
            def counter(increment=1):
                res = couner.counter
                counter.counter += increment
                return res
            counter.counter = 0
            return counter
        getrow = counter_factory(0)
        worksheet.write(0, 0, u"Информация об удовлетворении исковых требований за вред, причиненный в результате нарушения законодательства в области санитарно-эпидемиологического благополучия населения, охраны окружающей среды и природопользования, за  %s г. по полигону %s железной дороги" % (
            year1,
            rw_id.name_get()[0][1] or u'<Не указано>'
        ), workbook.title_format)

        getcol = counter_factory(0)
        worksheet.merge_range(2, getcol(0), 3, getcol(1), u"Показатель / наименование региональной дирекции, РЦКУ", header_format)
        vsego_col = getcol(1)
        worksheet.merge_range(2, vsego_col, 3, vsego_col, u"Всего", header_format)
        worksheet.merge_range(2, getcol(0), 3, getcol(0) + 1, u"Из них:", header_format)
        rcku_col = getcol(1)
        worksheet.write(2, rcku_col, u"РЦКУ", header_format)
        filial_col = getcol(1)
        worksheet.write(2, filial_col, u"Филиалы", header_format)

        # vsego_map = {}
        # rcku_map = {}
        # filial_map = {}
        def get_cdir(dep_id):
            if not dep_id or dep_id.short_name == u'ОАО "РЖД"':
                return False
            if dep_id in rzd_cdir_ids:
                return dep_id
            return get_cdir(dep_id.parent_id)
        for row_index, row in enumerate(first_col):
            worksheet.write(4 + row_index, 0, row[0], row[1])


        count = 0           # Количество предъявленных исков, всего
        count_rcku = 0      # Количество предъявленных исков, рцку
        count_rest = 0      # Количество предъявленных исков, филиалы

        count_obzh = 0      # Количество обжалованных исков, всего
        count_obzh_rcku = 0 # Количество обжалованных исков, рцку
        count_obzh_rest = 0 # Количество обжалованных исков, филиалы
        
        count_otme = 0       # Количество отмененных исков, всего
        count_otme_rcku = 0  # Количество отмененных исков, рцку
        count_otme_rest = 0  # Количество отмененных исков, филиалы
        
        count_vozm = 0      # Количество возмещенных исков, всего
        count_vozm_rcku = 0 # Количество возмещенных исков, рцку
        count_vozm_rest = 0 # Количество возмещенных исков, филиалы
        
        
        sum_pred = 0        # Сумма предъявленных исков, всего
        sum_pred_rcku = 0   # Сумма предъявленных исков, рцку
        sum_pred_rest = 0   # Сумма предъявленных исков, филиалы

        sum_obzh = 0        # Сумма обжалованных исков, всего
        sum_obzh_rcku = 0   # Сумма обжалованных исков, рцку
        sum_obzh_rest = 0   # Сумма обжалованных исков, филиалы
        
        sum_otme = 0         # Сумма отмененных исков, всего
        sum_otme_rcku = 0    # Сумма отмененных исков, рцку
        sum_otme_rest = 0    # Сумма отмененных исков, филиалы
        
        sum_vozm = 0        # Сумма возмещенных исков, всего
        sum_vozm_rcku = 0   # Сумма возмещенных исков, рцку
        sum_vozm_rest = 0   # Сумма возмещенных исков, филиалы
        
        
        count_log = 0       # Количество судебных решений, всего
        count_log_rcku = 0  # Количество судебных решений, рцку
        count_log_rest = 0  # Количество судебных решений, филиалы

        sum_flags = 0       # Сумма оплаченных исков, всего
        sum_flags_rcku = 0  # Сумма оплаченных исков, рцку
        sum_flags_rest = 0  # Сумма оплаченных исков, филиалы
        
        sum_flag1 = 0       # Сумма оплаченных исков по флагу 1, всего
        sum_flag1_rcku = 0  # Сумма оплаченных исков по флагу 1, рцку
        sum_flag1_rest = 0  # Сумма оплаченных исков по флагу 1, филиалы
        
        sum_flag2 = 0       # Сумма оплаченных исков по флагу 2, всего
        sum_flag2_rcku = 0  # Сумма оплаченных исков по флагу 2, рцку
        sum_flag2_rest = 0  # Сумма оплаченных исков по флагу 2, филиалы 

        for dep_index, dep_id in enumerate(rzd_cdir_ids):
            sud_filtered_cdir_ids = sud_ids.filtered(lambda sud: get_cdir(sud.department_id) == dep_id)
            sud_filtered_cdir_obzha_ids = sud_filtered_cdir_ids.filtered(lambda sud: sud.status == 'obzhal')
            sud_filtered_cdir_otmen_ids = sud_filtered_cdir_ids.filtered(lambda sud: sud.status == 'otmen')
            sud_filtered_cdir_vozme_ids = sud_filtered_cdir_ids.filtered(lambda sud: sud.status == 'vozme')
            sud_filtered_cdir_oplach_flags_ids = sud_filtered_cdir_ids.filtered(lambda sud: 'oplach' in sud.log_ids.mapped('status') and (sud.narushenie_ohrana or sud.narushenie_sanitar))
            count += len(sud_filtered_cdir_ids)
            count_obzh += len(sud_filtered_cdir_obzha_ids)
            count_otme += len(sud_filtered_cdir_otmen_ids)
            count_vozm += len(sud_filtered_cdir_vozme_ids)
            sum_pred += sum(sud_filtered_cdir_ids.mapped('cena_iska'))
            sum_obzh += sum(sud_filtered_cdir_obzha_ids.mapped('cena_iska'))
            sum_otme += sum(sud_filtered_cdir_otmen_ids.mapped('cena_iska'))
            sum_vozm += sum(sud_filtered_cdir_vozme_ids.mapped('cena_iska'))
            count_log += len(sud_filtered_cdir_ids.mapped('log_ids').filtered(lambda log: log.status not in ['na_obzh', 'vozme']))
            sum_flags += sum(sud_filtered_cdir_oplach_flags_ids.mapped('summa'))
            sum_flag1 += sum(sud_filtered_cdir_oplach_flags_ids.filtered(lambda sud: sud.narushenie_ohrana).mapped('summa'))
            sum_flag2 += sum(sud_filtered_cdir_oplach_flags_ids.filtered(lambda sud: sud.narushenie_sanitar).mapped('summa'))
            for sud in sud_filtered_cdir_ids:
                if sud.department_id.role == 'rcku':
                    count_rcku += 1
                    count_obzh_rcku += 1 sud.status == 'obzhal' else 0
                    count_otme_rcku += 1 sud.status == 'otmen' else 0
                    count_vozm_rcku += 1 sud.status == 'vozme' else 0
                    sum_pred_rcku += sud.cena_iska
                    sum_obzh_rcku += sud.cena_iska if sud.status == 'obzhal' else 0
                    sum_otme_rcku += sud.cena_iska if sud.status == 'otmen' else 0
                    sum_vozm_rcku += sud.cena_iska if sud.status == 'vozme' else 0
                    count_log_rcku += len(sud.log_ids.filtered(lambda log: log.status not in ['na_obzh', 'vozme']))
                    sum_flags_rcku += sud.summa if 'oplach' in sud.log_ids.mapped('status') and (sud.narushenie_ohrana or sud.narushenie_sanitar) else 0
                    sum_flag1_rcku += sud.summa if 'oplach' in sud.log_ids.mapped('status') and sud.narushenie_ohrana else 0
                    sum_flag2_rcku += sud.summa if 'oplach' in sud.log_ids.mapped('status') and sud.narushenie_sanitar else 0
                else:
                    count_rest += 1
                    count_obzh_rest += 1 sud.status == 'obzhal' else 0
                    count_otme_rest += 1 sud.status == 'otmen' else 0
                    count_vozm_rest += 1 sud.status == 'vozme' else 0
                    sum_pred_rest += sud.cena_iska
                    sum_obzh_rest += sud.cena_iska if sud.status == 'obzhal' else 0
                    sum_otme_rest += sud.cena_iska if sud.status == 'otmen' else 0
                    sum_vozm_rest += sud.cena_iska if sud.status == 'vozme' else 0
                    count_log_rest += len(sud.log_ids.filtered(lambda log: log.status not in ['na_obzh', 'vozme']))
                    sum_flags_rest += sud.summa if 'oplach' in sud.log_ids.mapped('status') and (sud.narushenie_ohrana or sud.narushenie_sanitar) else 0
                    sum_flag1_rest += sud.summa if 'oplach' in sud.log_ids.mapped('status') and sud.narushenie_ohrana else 0
                    sum_flag2_rest += sud.summa if 'oplach' in sud.log_ids.mapped('status') and sud.narushenie_sanitar else 0



            worksheet.write(5, getcol(1) + dep_index, cdir_count, row[1])
            
        # row 1
        worksheet.write(5, 1, count, workbook.cell_format)
        worksheet.write(5, 2, count_rcku, workbook.cell_format)
        worksheet.write(5, 3, count_rest, workbook.cell_format)
            
        # row 2
        worksheet.write(6, 1, count_obzh, workbook.cell_format)
        worksheet.write(6, 2, count_obzh_rcku, workbook.cell_format)
        worksheet.write(6, 3, count_obzh_rest, workbook.cell_format)
            
        # row 3
        worksheet.write(7, 1, count_otme, workbook.cell_format)
        worksheet.write(7, 2, count_otme_rcku, workbook.cell_format)
        worksheet.write(7, 3, count_otme_rest, workbook.cell_format)
            
        # row 4
        worksheet.write(8, 1, count_vozm, workbook.cell_format)
        worksheet.write(8, 2, count_vozm_rcku, workbook.cell_format)
        worksheet.write(8, 3, count_vozm_rest, workbook.cell_format)
            
        # row 5
        worksheet.write(9, 1, sum_pred, workbook.cell_format)
        worksheet.write(9, 2, sum_pred_rcku, workbook.cell_format)
        worksheet.write(9, 3, sum_pred_rest, workbook.cell_format)
            
        # row 6
        worksheet.write(10, 1, sum_obzh, workbook.cell_format)
        worksheet.write(10, 2, sum_obzh_rcku, workbook.cell_format)
        worksheet.write(10, 3, sum_obzh_rest, workbook.cell_format)
            
        # row 7
        worksheet.write(11, 1, sum_otme, workbook.cell_format)
        worksheet.write(11, 2, sum_otme_rcku, workbook.cell_format)
        worksheet.write(11, 3, sum_otme_rest, workbook.cell_format)
            
        # row 8
        worksheet.write(12, 1, sum_vozm, workbook.cell_format)
        worksheet.write(12, 2, sum_vozm_rcku, workbook.cell_format)
        worksheet.write(12, 3, sum_vozm_rest, workbook.cell_format)
            
        # row 9
        worksheet.write(13, 1, count_log, workbook.cell_format)
        worksheet.write(13, 2, count_log_rcku, workbook.cell_format)
        worksheet.write(13, 3, count_log_rest, workbook.cell_format)
            
        # row 10
        worksheet.write(14, 1, sum_flags, workbook.cell_format)
        worksheet.write(14, 2, sum_flags_rcku, workbook.cell_format)
        worksheet.write(14, 3, sum_flags_rest, workbook.cell_format)
            
        # row 11
        worksheet.write(15, 1, sum_flag1, workbook.cell_format)
        worksheet.write(15, 2, sum_flag1_rcku, workbook.cell_format)
        worksheet.write(15, 3, sum_flag1_rest, workbook.cell_format)
            
        # row 12
        worksheet.write(16, 1, sum_flag2, workbook.cell_format)
        worksheet.write(16, 2, sum_flag2_rcku, workbook.cell_format)
        worksheet.write(16, 3, sum_flag2_rest, workbook.cell_format)

        return workbook.get_response(filename)


        def row0(dep_id):
            count = 0
            count_rcku = 0
            count_cdir = 0
            for sud_id in sud_ids:
                cdir_id = get_cdir(sud_id.department_id)
                if dep_id == cdir_id:
                    count += 1
                if sud_id.department_id.role == 'rcku':
                    count_rcku += 1
                else:
                    count_cdir += 1
                logInfo("count=%s" % count)
                logInfo("count_rcku=%s" % count_rcku)
                logInfo("count_cdir=%s" % count_cdir)

            return count, count_rcku, count_cdir