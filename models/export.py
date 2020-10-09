# -*- coding: utf-8 -*-
from openerp import http, fields, api
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception, content_disposition
from io import BytesIO
import xlsxwriter
from collections import defaultdict, OrderedDict
from ..controllers.tab1 import *
from ..controllers.utils import *

def fdate(date_str=False):
    if not date_str:
        return ''
    # if not date_str:
    #     return u"«___»___________ 20___ г."
    date = fields.Date.from_string(date_str)
    # return u"«%02d»%s %d г." % (date.day, months[date.month], date.year)
    return u"%02d.%02d.%d" % (date.day, date.month, date.year)
    

def add_to_format(existing_format, dict_of_properties, workbook):
    """Give a format you want to extend and a dict of the properties you want to
    extend it with, and you get them returned in a single format"""
    new_dict = {}
    for key, value in existing_format.__dict__.iteritems():
        if (value != 0) and (value != {}) and (value != None):
            new_dict[key] = value
    del new_dict['escapes']

    return(workbook.add_format(dict(new_dict.items() + dict_of_properties.items())))

class MyWorkbook(xlsxwriter.Workbook):

    def add_to_format(self, existing_format, dict_of_properties):
        """Give a format you want to extend and a dict of the properties you want to
        extend it with, and you get them returned in a single format"""
        new_dict = {}
        for key, value in existing_format.__dict__.iteritems():
            if (value != 0) and (value != {}) and (value != None):
                new_dict[key] = value
        del new_dict['escapes']

        return(self.add_format(dict(new_dict.items() + dict_of_properties.items())))

    def __init__(self, *args, **kwargs):
        self.doc_bytes = BytesIO()
        super(MyWorkbook, self).__init__(self.doc_bytes, *args, **kwargs)
        self.base_format = self.add_format({
            'font': 'Times New Roman',
            'text_wrap': True,
            'border': 0,
        })
        self.title_format = self.add_to_format(self.base_format, {
            'bold': True,
            'align': 'center',
            'size': 14,
        })
        self.cell_format = self.add_to_format(self.base_format, {
            'border': 1,
            'align': 'center',
        })
        self.bold_cell_format = self.add_to_format(self.base_format, {
            'border': 1,
            'bold': True
        })
        self.header_format = self.add_to_format(self.base_format, {
            'bold': True,
            'align': 'center',
            'border': 2,
            'size': 12,
        })
    
    def get_response(self, filename):
        return request.make_response(self.close_and_read(), [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', content_disposition(filename))
        ])
    def close_and_read(self):
        self.close()
        self.doc_bytes.seek(0)
        return self.doc_bytes.read()
    
from openerp import models, pooler
class ir_actions_report_xml(models.Model):
    _inherit = 'ir.actions.report.xml'

    def _check_selection_field_value(self, cr, uid, field, value, context=None):
        if field == 'report_type' and value == 'xlsx':
            return
        return super(ir_actions_report_xml, self)._check_selection_field_value(
            cr, uid, field, value, context=context)

from ....report.report_sxw import report_sxw
class report_xls(report_sxw):
    def create(self, cr, uid, ids, data, context=None):
        self.pool = pooler.get_pool(cr.dbname)
        self.cr = cr
        self.uid = uid
        report_obj = self.pool.get('ir.actions.report.xml')
        report_ids = report_obj.search(
            cr, uid, [('report_name', '=', self.name[7:])], context=context)
        if report_ids:
            report_xml = report_obj.browse(
                cr, uid, report_ids[0], context=context)
            if report_xml.report_type == 'xlsx':
                self.title = report_xml.report_file
                workbook = MyWorkbook()
                self.pool[context['active_model']].do_print_xlsx(cr, uid, [context.get('active_ids')[0]], workbook)
                return workbook.close_and_read(), 'xlsx'
        return super(report_xls, self).create(cr, uid, ids, data, context)

report_xls('report.pid.pret_isk.xlsx',
    'eco.pret_isk',0)
