# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models

class FormZO1(models.Model):
    _inherit='eco.form.zo_1'

    pid_sum_san = fields.Float(u"Выплачено административных штрафов за нарушения в области санитарно-эпидемиологического благополучия населения")
    pid_sum_not_san = fields.Float(u"Выплачено административных штрафов за нарушения в области охраны окружающей среды и природопользования")
    sud_sum_san = fields.Float(u"Выплачено в целях удовлетворения исковых требований в виде денежной компенсации вреда окружающей среде, причиненного нарушением законодательства в области охраны окружающей среды")
    sud_sum_not_san = fields.Float(u"Выплачено в целях удовлетворения исковых требований в виде денежной компенсации вреда вследствие нарушения санитарно-эпидемиологического законодательства")
    pull_from_r9 = fields.Boolean(u"Перенести остатки, штрафы и иски по предприятию")
    diff_pid_sum_san = fields.Float(u"Выплачено административных штрафов за нарушения в области санитарно-эпидемиологического благополучия населения")
    diff_pid_sum_not_san = fields.Float(u"Выплачено административных штрафов за нарушения в области охраны окружающей среды и природопользования")
    diff_sud_sum_san = fields.Float(u"Выплачено в целях удовлетворения исковых требований в виде денежной компенсации вреда окружающей среде, причиненного нарушением законодательства в области охраны окружающей среды")
    diff_sud_sum_not_san = fields.Float(u"Выплачено в целях удовлетворения исковых требований в виде денежной компенсации вреда вследствие нарушения санитарно-эпидемиологического законодательства")

    @api.onchange('department_id')
    def _onchange_department_id_from_pid(self):
        if self.department_id:
            year1 = self.year
            year2 = self.year
            month1 = (int(self.quarter) - 1) * 3 + 1
            month2 = month1 + 3
            if month2 > 12:
                year2 = str(int(year1) + 1)
                month2 -= 12
            pid_ids = self.env['eco.pret_isk'].search([
                ('postanovlenie_notkodex_date', '>=', "%s-%s-01" % (year1, month1)),
                ('postanovlenie_notkodex_date', '<', "%s-%s-01" % (year2, month2))
            ])
            sud_ids = self.env['eco.pret_isk.sud'].search([
                ('data_predyavlenia', '>=', "%s-%s-01" % (year1, month1)),
                ('data_predyavlenia', '<', "%s-%s-01" % (year2, month2)),
                ('department_id','=',self.department_id.id)
            ])
            zo1_ids = self.env[self._name].search([
                ('year','=',self.year),
                ('quarter','=',self.quarter),
                ('department_id','=',self.department_id.id),
            ])
            self.pid_sum_san = sum(pid_ids.filtered(lambda pid: pid.postanovlenie_is_accepted != '2' and pid.postanovlenie_iskodex_statia_kind == '1').mapped('v1_01').mapped('summa4'))
            self.pid_sum_not_san = sum(pid_ids.filtered(lambda pid: pid.postanovlenie_is_accepted != '2' and pid.postanovlenie_iskodex_statia_kind == '2').mapped('v1_01').mapped('summa4'))
            self.sud_sum_san = sum(sud_ids.filtered(lambda sud: sud.category == 'environ' and sud.is_payed()).mapped('summa'))
            self.sud_sum_not_san = sum(sud_ids.filtered(lambda sud: sud.category == 'sanitar' and sud.is_payed()).mapped('summa'))
            self.diff_pid_sum_san = self.pid_sum_san - sum(zo1_ids.mapped('r9_1_1'))
            self.diff_pid_sum_not_san = self.pid_sum_not_san - sum(zo1_ids.mapped('r9_1_2'))
            self.diff_sud_sum_san = self.sud_sum_san - sum(zo1_ids.mapped('r9_2_1'))
            self.diff_sud_sum_not_san = self.sud_sum_not_san - sum(zo1_ids.mapped('r9_2_2'))
        else:
            self.pid_sum_san = 0
            self.pid_sum_not_san = 0
            self.sud_sum_san = 0
            self.sud_sum_not_san = 0
            self.diff_pid_sum_san = 0
            self.diff_pid_sum_not_san = 0
            self.diff_sud_sum_san = 0
            self.diff_sud_sum_not_san = 0
    
    @api.multi
    def write(self, new_vals):
        pull_from_r9 = new_vals.pop('pull_from_r9', False)
        if pull_from_r9:
            new_vals['r9_1_1'] = new_vals.get('diff_pid_sum_san', new_vals.get('r9_1_1', self.r9_1_1))
            new_vals['r9_1_2'] = new_vals.get('diff_pid_sum_not_san', new_vals.get('r9_1_2', self.r9_1_2))
            new_vals['r9_2_1'] = new_vals.get('diff_sud_sum_san', new_vals.get('r9_2_1', self.r9_2_1))
            new_vals['r9_2_2'] = new_vals.get('diff_sud_sum_not_san', new_vals.get('r9_2_2', self.r9_2_2))
        res = super(FormZO1, self).write(new_vals)

        return res