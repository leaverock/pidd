# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models
from ..util import logInfo, log

_v1_08_NADZ = [("nadz", u"Росприроднадзор")]
_v1_08_PROC = [("proc", u"Прокуратура")]
_v1_08_SELECTION = _v1_08_NADZ + _v1_08_PROC
_v1_08_SELECTION_DICT = dict(_v1_08_SELECTION)

_PRET_STATE_ACCEPTED = [("accepted", u"Принято")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Есть нарушения")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_NOT_LOCATED = [("not_located", u"Не обнаружено")]
_PRET_STATE_SELECTION = _v1_08_NADZ + _v1_08_PROC
_PRET_STATE_SELECTION_DICT = dict(_PRET_STATE_SELECTION)

class Problem(models.Model):
    if log ['models']: logInfo('***** pid.models.Problem: class enter')
    _name = 'eco.pret_isk.problems'
    _description = u'Проблематика ПИД'
    _rec_name="v0_01"
    name = fields.Char(u"name", default=u'Проблематика ПИД')
    v0_01 = fields.Char(u"Проблема", required=True)


class Pid(models.Model):
    if log ['models']: logInfo('***** pid.models.Pid: class enter')
    _name = 'eco.pret_isk'
    _description = u'Претензионно-исковая деятельность'
    name = fields.Char(u"_rec_name", default=u'ПИД')
    creator_department_id = fields.Many2one('eco.department', related="create_uid.department_id")
    # pret_state = fields.Selection(_PRET_STATE_SELECTION_DICT)


    def search(self, cr, uid, domain, *args, **kwargs):
        '''
        В журнале у пользователя должны отображаться только отчёты его предприятия и дочерних
        '''
        dep_ids = self.pool['eco.department'].search(cr, uid, [])
        domain += [('creator_department_id', 'in', dep_ids)]
        res = super(Pid, self).search(cr, uid, domain, *args, **kwargs)
        return res

    ##############################################################################################################
    #
    #  Переменные вкладки "1. Основные сведения" представления' модуля eco.pret_isk'
    #
    ##############################################################################################################
    v1_01 = fields.Many2many(
        'eco.department',
        string=u"Предприятия и их полигоны"
    )
    v1_02 = fields.Text(u'Основание проведения проверки', required=True)
    v1_03 = fields.Selection([("plan_doc", u"Плановая документарная"), ("plan_out", u"Плановая выездная"),
        ("out_plan_doc", u"Внеплановая документарная"), ("out_plan_out", u"Внеплановая выездная")], string=u'Вид проверки', default="plan_doc")
    v1_04 = fields.Char(u"Исходящий номер", required=True)
    v1_05 = fields.Char(u"Номер входящего", required=True)
    v1_06 = fields.Date(u'Дата поступления в ОАО "РЖД"', required=True)
    v1_07 = fields.Text(u'Краткое содержание документа', required=True)
    v1_08 = fields.Selection(_v1_08_SELECTION, string=u'ФОИВ осуществляющий проверку', default=_v1_08_NADZ[0][0])
    v1_09 = fields.Selection([("pric", u"Приказ"), ("rasp", u"Распоряжение"),], string=u'Наименования документа ', default="pric")
    v1_10 = fields.Date(u'Плановый срок исполнения', required=True)
    v1_11 = fields.One2many('eco.pret_isk.attached_files', 'pid_id', string=u'Документы', domain=[('tab', '=', '1'), ])

    ##############################################################################################################
    #
    #  Переменные вкладки "2. Проблематика" модуля eco.pret_isk'
    #
    ##############################################################################################################
    akt_file = fields.Binary(u"Акт проверки")
    akt_name = fields.Char(u"Акт проверки")

    akt_date = fields.Date(u'Дата составления акта')
    akt_num = fields.Char(u"Номер акта")
    akt_has_narush = fields.Boolean(u'Есть нарушения')

    act_problematica = fields.Many2one('eco.pret_isk.problems', string=u"Проблематика")
    akt_ustranenie_file = fields.Binary(u"Предписание об устранении")
    akt_ustranenie_name = fields.Char(u"Предписание об устранении")

    akt_ustranenie_item_ids = fields.One2many('eco.pret_isk.predpisanie', 'pid_id', string=u"Пункты предписания")

    akt_vozrazhenie_file = fields.Binary(u"Возражение")
    akt_vozrazhenie_name = fields.Char(u"Возражение")

    akt_is_accepted = fields.Selection([('1', u'Принято к исполнению'), ('2', u'Обжалование'),], default="1")

    akt_ustranenie_exec_file = fields.Binary(u"Устранение")
    akt_ustranenie_exec_name = fields.Char(u"Устранение")

    akt_predpisanie_state = fields.Selection([('1', u'Отмена предписания'), ('2', u'Выполнение предписания'),], default="2")

    akt_predpisanie_cancel_file = fields.Binary(u"Отмена предписания")
    akt_predpisanie_cancel_name = fields.Char(u"Отмена предписания")

    akt_predpisanie_exec_file = fields.Binary(u"Выполнение предписания")
    akt_predpisanie_exec_name = fields.Char(u"Выполнение предписания")



    ##############################################################################################################
    #
    #  Переменные вкладки "3. Протокол' модуля eco.pret_isk'
    #
    ##############################################################################################################
    protokol_file = fields.Binary(u"Протокол")
    protokol_filename = fields.Char(u"Протокол")
    protokol_description = fields.Text(u"Краткая суть")
    #protokol_date = fields.Date(u"Дата")
    protokol_zakon = fields.Selection([('1', u'КОаП РФ'), ('2', u'Иное законодательство'),], default="1")
    protokol_iskodex_1 = fields.Integer(u"Ст. №")
    protokol_iskodex_2 = fields.Integer(u"ч. №")
    protokol_iskodex_3 = fields.Integer(u"п. №")
    protokol_iskodex_4 = fields.Integer(u"пп. №")

    protokol_iskodex_5 = fields.Date(u"Дата возбуждения дела об административном правонарушении")
    protokol_iskodex_6 = fields.Float(u"Сумма взыскания")
    protokol_iskodex_7 = fields.Date(u"Дата")

    protokol_notkodex_kind = fields.Selection(
        [
            ('1', u'Закон'),
            ('2', u'Указ'),
            ('3', u'Постановление'),
            ('4', u'Другое'),
        ],
        default="2",
        string=u"Вид регионального законодательного акта"
    )
    protokol_notkodex_num = fields.Char(u"Номер")
    protokol_notkodex_name = fields.Char(u"Наименование")
    protokol_notkodex_date = fields.Date(u"Дата")
    protokol_notkodex_summa = fields.Float(u"Сумма взыскания")

    protokol_is_accepted = fields.Selection([('1', u'Принято к исполнению'), ('2', u'Обжалование и отмена'),
                                             ('3', u'Обжалование и выполнение'),], default="1",
                                            string=u"Исполнение и обжалование")

    protokol_exec_file = fields.Binary(u"Принято к исполнению")
    protokol_exec_name = fields.Char(u"Принято к исполнению")

    protokol_cancel_file = fields.Binary(u"Обжалование и отмена")
    protokol_cancel_name = fields.Char(u"Обжалование и отмена")

    protokol_obj_exec_file = fields.Binary(u"Обжалование и выполнение")
    protokol_obj_exec_name = fields.Char(u"Обжалование и выполнение")

    
    ##############################################################################################################
    #
    #  Переменные вкладки "4. Постановление' модуля eco.pret_isk'
    #
    ##############################################################################################################
    postanovlenie_file = fields.Binary(u"Предписание")
    postanovlenie_filename = fields.Char(u"Предписание")
    postanovlenie_description = fields.Text(u"Краткая суть")
    postanovlenie_date = fields.Date(u"Дата")
    postanovlenie_zakon = fields.Selection([('1', u'КОаП РФ'), ('2', u'Иное законодательство'),], default="1")

    postanovlenie_iskodex_1 = fields.Integer(u"Ст. №")
    postanovlenie_iskodex_2 = fields.Integer(u"ч. №")
    postanovlenie_iskodex_3 = fields.Integer(u"п. №")
    postanovlenie_iskodex_4 = fields.Integer(u"пп. №")
    postanovlenie_iskodex_5 = fields.Date(u"Дата возбуждения дела об административном правонарушении")
    postanovlenie_iskodex_6 = fields.Float(u"Сумма взыскания")

    postanovlenie_notkodex_kind = fields.Selection(
        [
            ('1', u'Закон'),
            ('2', u'Указ'),
            ('3', u'Постановление'),
            ('4', u'Другое'),
        ],
        default="2",
        string=u"Вид регионального законодательного акта"
    )
    postanovlenie_notkodex_num = fields.Char(u"Номер")
    postanovlenie_notkodex_name = fields.Char(u"Наименование")
    postanovlenie_notkodex_date = fields.Date(u"Дата")
    postanovlenie_notkodex_summa = fields.Float(u"Сумма взыскания")

    #postanovlenie_descr_easd = fields.Text(u"ЕАСД ОАО 'РЖД'")
    postanovlenie_num_easd = fields.Char(u"Номер")
    postanovlenie_date_easd = fields.Date(u"Дата")
    
    postanovlenie_is_accepted = fields.Selection([('1', u'Принято к исполнению'), ('2', u'Обжалование и отмена'),
                                             ('3', u'Обжалование и выполнение'),], default="1",
                                            string=u"Исполнение и обжалование")

    postanovlenie_exec_file = fields.Binary(u"Принято к исполнению")
    postanovlenie_exec_name = fields.Char(u"Принято к исполнению")

    postanovlenie_cancel_file = fields.Binary(u"Обжалование и отмена")
    postanovlenie_cancel_name = fields.Char(u"Обжалование и отмена")

    postanovlenie_obj_exec_file = fields.Binary(u"Обжалование и выполнение")
    postanovlenie_obj_exec_name = fields.Char(u"Обжалование и выполнение")

    @api.multi
    def get_pret_state(self):
        self.ensure_one()
        if self.postanovlenie_is_accepted == '1':
            res = u"Исполнение постановления"
        elif self.postanovlenie_is_accepted == '2':
            res = u"Отмена постановления"
        elif self.postanovlenie_is_accepted == '3':
            res = u"Выполнение постановления"
        elif self.protokol_is_accepted == '1':
            res = u"Исполнение протокола"
        elif self.protokol_is_accepted == '2':
            res = u"Отмена протокола"
        elif self.protokol_is_accepted == '3':
            res = u"Выполнение протокола"
        elif self.akt_is_accepted == '1':
            res = u"Исполнение предписания"
        elif self.akt_is_accepted == '2':
            if self.akt_predpisanie_state == '1':
                res = u"Отмена предписания"
            else:
                res = u"Выполнение предписания"
        else:
            res = u"Принято"

        return res

    tab1_done = fields.Boolean()
    tab2_done = fields.Boolean()
    tab3_done = fields.Boolean()
    tab4_done = fields.Boolean()
    can_see_unlock_tab1 = fields.Boolean(compute="_compute_can_see_unlock_tab")
    can_see_unlock_tab2 = fields.Boolean(compute="_compute_can_see_unlock_tab")
    can_see_unlock_tab3 = fields.Boolean(compute="_compute_can_see_unlock_tab")
    can_see_unlock_tab4 = fields.Boolean(compute="_compute_can_see_unlock_tab")

    @api.multi
    def set_tab_done(self, tab):
        self.ensure_one()
        setattr(self, 'tab%s_done' % tab, not getattr(self, 'tab%s_done' % tab))

    @api.multi
    @api.depends('tab1_done','tab2_done','tab3_done','tab4_done')
    def _compute_can_see_unlock_tab(self):
        dep_ids = self.env['eco.department'].search([])
        for rec in self:
            if self.env.user.id == 1 or (self.env.user.user_role == 'dep_eng' and rec.create_uid.department_id in dep_ids):
            # if self.env.user.id == 1 or self.env.user.department_id == rec.create_uid.department_id.parent_id or self.env.user == rec.create_uid:
                for d in range(1, 5):
                    setattr(rec, 'can_see_unlock_tab%d' % d, getattr(rec, 'tab%d_done' % d))
            else:
                for d in range(1, 5):
                    setattr(rec, 'can_see_unlock_tab%d' % d, False)



##############################################################################################################
#
#  misk classes
#
##############################################################################################################
class AttachedFiles(models.Model):
    _name = 'eco.pret_isk.attached_files'
    _rec_name = 'name'

    tab = fields.Char(string=u'Номер вкладки', default="1")
    name = fields.Char(string=u'Имя файла', required=True)
    pid_id = fields.Many2one('eco.pret_isk', string=u'Прикрепленные файлы')
    file = fields.Binary(u'Файл', required=True)


class Predpisanie(models.Model):
    _name = 'eco.pret_isk.predpisanie'

    pid_id = fields.Many2one('eco.pret_isk')
    name = fields.Char(string=u'Описание пункта предписания')
    num = fields.Integer(string=u'Номер пункта предписания')
    deadline = fields.Date(u'Срок исполнения', required=True)
