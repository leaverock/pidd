# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models

'''
FROM

class ProizvControlExport(models.TransientModel):
    _name='eco.proizv.control.export.wz'
    _description=u'Визард для экспорта производственного контроля'

    def _default_decklarations(self):
        return self.env['eco.proizv.control'].browse(self._context.get('active_ids', []))[0]

    proizv_control_ids = fields.Many2many('eco.proizv.control', string=u'произв. контроль для экспорта',
        required=True, default=_default_decklarations)

    @api.multi
    def export_excel(self):
        for rec in self:
            return {
                'type' : 'ir.actions.act_url',
                'url': '/eco_proizv_control/export_proizv_control_xlsx?id=%s&filename=proizv_control.xlsx' % (
                    str(rec.id),
                ),
                'target': 'self',
            }

TO
see after

BY

#class 
ProizvControlExport                 PID_Export    
eco.proizv.control.export.wz        eco.pret_isk.export.wz
eco.proizv.control                  eco.pret_isk
proizv_control_ids                  pret_isk_ids     
        
#def export_excel 
/eco_proizv_control/                /eco_pret_isk/
export_proizv_control_xlsx          export_pret_isk_xlsx                    
proizv_control                      pret_isk              
'''


class PID_Export(models.TransientModel):
    _name = 'eco.pret_isk.export.wz'
    _description = u'Визард для экспорта форм претензионно-исковой деятельности'

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

