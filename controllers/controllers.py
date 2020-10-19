# -*- coding: utf-8 -*-
from openerp import http, exceptions
from openerp.addons.web.controllers.main import serialize_exception, content_disposition
from io import BytesIO
import xlsxwriter
from ..util import log, logInfo
from utils import get_report_data_from_record
from ..controllers.tab_single import tab1_str, table_1_head, table_1_body
from ..controllers.utils import tab1_width, cell_width

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

        worksheet = workbook.add_worksheet(u'Штрафы за квартал')
        worksheet.set_column(0, tab1_width - 1, cell_width)
        r = tab1_str(workbook, worksheet, 0, u'Информация о предъявленных административных штрафах юридическим лицам за %s квартал %s года' % (wz.quarter, wz.year))
        r, col_widths = table_1_head(workbook, worksheet, r)
        for pid in pid_ids:
            r = table_1_body(workbook, worksheet, r, get_report_data_from_record(pid), col_widths)

        workbook.close()
        doc_bytes.seek(0)

        return request.make_response(doc_bytes.read(),
                                     [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                      ('Content-Disposition', content_disposition(filename))])

