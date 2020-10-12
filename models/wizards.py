# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models
from datetime import datetime

def get_years_list(*a, **b):
    y = datetime.now().year
    res = [(str(o), str(o)+u'г.') for o in range(y-2, y+3, 1)]
    res.reverse()
    return res

def default_year(*a):
    return str(datetime.now().year)
#_REPORT_IS_ANNUAL = [('annual', u'Сформировать отчёт за год')]
#_REPORT_IS_QUARTER = [('quarter', u'Сформировать отчёт за квартал')]
#_SELECTION_REPORT_PERIOD = _REPORT_IS_ANNUAL + _REPORT_IS_QUARTER


class PID_Export(models.TransientModel):
    _name = 'eco.pret_isk.export.wz'
    _description = u'Визард для экспорта текущей формы претензионно-исковой деятельности'

    def _default_decklarations(self):
        return self.env['eco.pret_isk'].browse(self._context.get('active_ids', []))[0]

    pret_isk_ids = fields.Many2many('eco.pret_isk', string=u'претенз.-иск. деятельность для экспорта',
                                          required=True, default=_default_decklarations)

    @api.multi
    def export_excel(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_url',
                'url': '/eco_pret_isk/export_pret_isk_xlsx?id=%s&filename=pret_isk.xlsx' % (str(rec.id),),
                'target': 'self',
            }

'''
class PidExportMulti(models.TransientModel):
    _name='eco.pid.multi.wz'
    _description = u'Визард для экспорта форм за определёный период претензионно-исковой деятельности'

    name = fields.Char(compute="_compute_name")
    year = fields.Selection(get_years_list, u"Выберите год отчёта", default=default_year)
    report_period = fields.Selection(_SELECTION_REPORT_PERIOD, u"Период отчёта", default=_REPORT_IS_QUARTER[0][0])
    quarter = fields.Selection([('1','I'),('2','II'),('3','III'),('4','IV')], u'Квартал')
    date_start = fields.Date()
    date_end   = fields.Date()

    @api.multi
    def _compute_name(self):
        for rec in self:
            rec.name = ''

    @api.multi
    def export_excel(self):
        self.ensure_one()
        return {
            'type' : 'ir.actions.act_url',
            'url': '/pid/export_multi?id=%s&filename=%s' % (
                self.id,
                "P14Export.xlsx",
            ),
            'target': 'self',
        }
'''

class PidExportMulti(models.TransientModel):
    _name='eco.pid.multi.wz'
    _description = u'Визард для экспорта форм за определёный период претензионно-исковой деятельности'

    #name = fields.Char(compute="_compute_name")
    year = fields.Selection(get_years_list, u"Выберите год отчёта", default=default_year)
    #report_period = fields.Selection(_SELECTION_REPORT_PERIOD, u"Период отчёта", default=_REPORT_IS_QUARTER[0][0])
    quarter = fields.Selection([('1','I'),('2','II'),('3','III'),('4','IV')], u'Квартал')
    #date_start = fields.Date()
    #date_end   = fields.Date()

    # @api.multi
    # def _compute_name(self):
    #     for rec in self:
    #         rec.name = ''

    @api.multi
    def export_excel(self):
        self.ensure_one()
        return {
            'type' : 'ir.actions.act_url',
            'url': '/pid/export_multi?id=%s&filename=%s' % (
                self.id,
                "pret_isk_multi.xlsx",
            ),
            'target': 'self',
        }