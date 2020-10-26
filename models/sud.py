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
_CATEGORY_SELECTION = [
    ('environ', u'Нарушения законодательства в области охраны окружающей среды'),
    ('sanitar', u'Нарушения  в области санитарного законодательства'),
    ('moral', u'Нарушения личных неимущественных прав (Моральный вред)'),
]
_NARUSHENIE_SELECTION = [
    ('ohrana', u'Нарушение законодательства в области охраны окружающей среды'),
    ('sanitar', u'Нарушение санитарного законодательства'),
]

class SudebnayaRabota(models.Model):
    _name='eco.pret_isk.sud'
    _description=u'Судебная работа'
    _rec_name='data_predyavlenia'

    data_predyavlenia = fields.Date(u"Дата предъявления судебного иска")
    department_id = fields.Many2one('eco.department', u"Подразделение", required=True, default=lambda self: self.env.user.department_id)
    kto_predyavil = fields.Selection([
        ('fiz', u"Физическое лицо"),
        ('yur', u"Юридическое лицо"),
        ('ros', u"Росприроднадзор (Государственный орган)"),
        ('pro', u"Прокуратура (Государственный орган)")
    ], u"Кто предъявил")
    predmet_iska = fields.Char(u"Предмет иска (требования истца об устранении нарушения права)")
    osnovanie_iska = fields.Text(u"Основание иска (отдельные нормы закона и юридические факты, на которых основаны требования искового заявления)")
    category = fields.Selection(_CATEGORY_SELECTION, u"Категория", required=True)
    cena_iska = fields.Float(u"Цена судебного иска, руб", (10, 3))
    meropriyatie = fields.Text(u"Мероприятие по устранению нарушений")
    state = fields.Selection(_STATE_SELECTION, u"Текущая ситуация")

    # data_napravleniya = fields.Date(u"Дата направления",    states={'invisible':['na_obzh']})
    # kakoy_sud = fields.Char(u"Какой суд",                   states={'invisible':['na_obzh', 'otmen']})
    # summa = fields.Float(u"Сумма, тыс руб", (10, 3),        states={'invisible':['na_obzh', 'obzhal', 'otmen', 'vozme', 'oplach']})
    # file = fields.Char(u"Файл",                             states={'invisible':['na_obzh', 'obzhal', 'otmen', 'vozme', 'oplach']})
    # filename = fields.Char(u"Имя файла",                    states={'invisible':['na_obzh', 'obzhal', 'otmen', 'vozme', 'oplach']})
    # rekvizity = fields.Char(u"Реквизиты документа",         states={'invisible':['vozme', 'oplach']})
    # kem_obzhalovan = fields.Char(u"Кем",                    states={'invisible':['vozme', 'oplach']})
    data_napravleniya = fields.Date(u"Дата направления",    states={False:[('invisible',1)], 'obzhal':[('invisible',1)], 'otmen':[('invisible',1)], 'vozme':[('invisible',1)], 'oplach':[('invisible',1)], })
    kakoy_sud = fields.Char(u"Какой суд",                   states={False:[('invisible',1)], 'obzhal':[('invisible',1)], 'vozme':[('invisible',1)], 'oplach':[('invisible',1)], })
    summa = fields.Float(u"Сумма, тыс руб", (10, 3),        states={False:[('invisible',1)],})
    file = fields.Binary(u"Файл",                           states={False:[('invisible',1)],})
    filename = fields.Char(u"Имя файла",                    states={False:[('invisible',1)],})
    rekvizity = fields.Char(u"Реквизиты документа",         states={False:[('invisible',1)], 'na_obzh':[('invisible',1)], 'obzhal':[('invisible',1)], 'otmen':[('invisible',1)], })
    kem_obzhalovan = fields.Char(u"Кем",                    states={False:[('invisible',1)], 'na_obzh':[('invisible',1)], 'obzhal':[('invisible',1)], 'otmen':[('invisible',1)], })

    log_ids = fields.One2many('eco.pret_isk.sud.log', 'sud_id', u"Логи", readonly=True)

    @api.multi
    def write(self, new_vals):
        state = new_vals.get('state', False)
        summa = new_vals.get('summa', False)
        # при изменении суммы или состояния
        if state or summa:
            for rec in self:
                # если сумма или состояние стали новыми
                if rec.state != state or rec.summa != summa:
                    # создаем запись в логе
                    self.env['eco.pret_isk.sud.log'].create({
                        'sud_id': rec.id,
                        'state': new_vals.get('state', rec.state),
                        'summa': new_vals.get('summa', rec.summa),
                    })
        res = super(SudebnayaRabota, self).write(new_vals)
        return res
    
    @api.model
    def create(self, vals):
        res = super(SudebnayaRabota, self).create(vals)
        self.env['eco.pret_isk.sud.log'].create({
            'sud_id': res.id,
            'state': vals.get('state', False),
            'summa': vals.get('summa', False),
        })
        return res

    @api.multi
    def get_payed_sum(self):
        u"""
        Получить последнюю оплаченную сумму из истории, после которой не было статуса отменён
        """
        res = 0
        for rec in self:
            log_ids = rec.log_ids.sorted(key=lambda log: log.create_date)
            otmen_index = -1
            oplach_index = -1
            for log_index, log in enumerate(log_ids):
                if log.state == 'otmen':
                    otmen_index = log_index
                elif log.state == 'oplach':
                    oplach_index = log_index
            if oplach_index > otmen_index:
                res += log_ids[oplach_index].summa
            # if 'oplach' not in statuses or 'oplach' in statuses and 'otmen' in statuses and statuses.index('oplach') >= statuses.index('otmen'):
            #     res = False
            #     break

        return res


class Log(models.Model):
    _name='eco.pret_isk.sud.log'
    _description=u'Лог по судебной работе'
    _rec_name='state'

    sud_id = fields.Many2one('eco.pret_isk.sud')

    state = fields.Selection(_STATE_SELECTION, u"Статус")
    summa = fields.Float(u"Сумма, тыс руб", (10, 3))
