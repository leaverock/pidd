# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models
from ..util import logInfo, log

_STATE_SELECTION = [
        ('na_obzh', u'На обжаловании'),
        ('obzhal', u'Обжалован'),
        ('otmen', u'Отменен'),
        ('vozme', u'Возмещен'),
        ('oplach', u'Оплачен'),
    ]

class SudebnayaRabota(models.Model):
    _name='eco.pret_isk.sud'
    _description=u'Судебная работа'
    _rec_name='data_predyavlenia'

    data_predyavlenia = fields.Date(u"Дата предъявления судебного иска")
    kto_predyavil = fields.Selection([
        ('fiz', u"Физическое лицо"),
        ('yur', u"Юридическое лицо"),
        ('ros', u"Росприроднадзор (Государственный орган)"),
        ('pro', u"Прокуратура (Государственный орган)")
    ], u"Кто предъявил")
    predmet_iska = fields.Char(u"Предмет иска (требования истца об устранении нарушения права)")
    osnovanie_iska = fields.Text(u"Основание иска (отдельные нормы закона и юридические факты, на которых основаны требования искового заявления)")
    cena_iska = fields.Float(u"Цена судебного иска, руб", (10, 3))
    meropriyatie = fields.Text(u"Мероприятие по устранению нарушений")
    category = fields.Char(u"Категория")
    state = fields.Selection(_STATE_SELECTION, u"Текущая ситуация")

    data_napravleniya = fields.Date(u"Дата направления",    states=['na_obzh'])
    kakoy_sud = fields.Char(u"Какой суд",                   states=['na_obzh', 'otmen'])
    summa = fields.Float(u"Сумма, тыс руб", (10, 3),        states=['na_obzh', 'obzhal', 'otmen', 'vozme', 'oplach'])
    file = fields.Char(u"Файл",                             states=['na_obzh', 'obzhal', 'otmen', 'vozme', 'oplach'])
    filename = fields.Char(u"Имя файла",                    states=['na_obzh', 'obzhal', 'otmen', 'vozme', 'oplach'])
    rekvizity = fields.Char(u"Реквизиты документа",         states=['vozme', 'oplach'])
    kem_obzhalovan = fields.Char(u"Кем",                    states=['vozme', 'oplach'])

    log_ids = fields.One2many('eco.pret_isk.sud.log', 'sud_id', u"Логи")

    @api.multi
    def write(self, new_vals):
        res = super(SudebnayaRabota, self).write(new_vals)
        for rec in self:
            self.env['eco.pret_isk.sud.log'].create({
                'sud_id': rec.id,
                'state': new_vals.get('state', False),
                'summa': new_vals.get('summa', False),
            })
        return res
    
    @api.model
    def create(self, vals):
        res = super(SudebnayaRabota, self).create(vals)
        self.env['eco.pret_isk.sud.log'].create({
            'sud_id': rec.id,
            'state': vals.get('state', False),
            'summa': vals.get('summa', False),
        })
        return res


class Log(models.Model):
    _name='eco.pret_isk.sud.log'
    _description=u'Лог по судебной работе'
    _rec_name='state'

    sud_id = fields.Many2one('eco.pret_isk.sud')

    state = fields.Selection(_STATE_SELECTION, u"Статус")
    summa = fields.Float(u"Сумма, тыс руб", (10, 3))
