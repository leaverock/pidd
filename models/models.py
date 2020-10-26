# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import api, exceptions, fields, models
from ..util import logInfo, log
from ..controllers.tab_single import *
from ..controllers.utils import *

_v1_08_NADZ = [("nadz", u"Росприроднадзор")]
_v1_08_PROC = [("proc", u"Прокуратура")]
_v1_08_SELECTION = _v1_08_NADZ + _v1_08_PROC
_v1_08_SELECTION_DICT = dict(_v1_08_SELECTION)

_PRET_STATE_SELECTION = _v1_08_NADZ + _v1_08_PROC
_PRET_STATE_SELECTION_DICT = dict(_PRET_STATE_SELECTION)

help_mark = u'<span>?</span>'


class Pid(models.Model):
    _name = 'eco.pret_isk'
    _description = u'Претензионно-исковая деятельность'
    name = fields.Char(u"_rec_name", default=u'ПИД')
    creator_department_id = fields.Many2one('eco.department', related="create_uid.department_id")

    @api.multi
    def download_help(self):
        self.ensure_one()
        return  {
                'type' : 'ir.actions.act_url',
                'url': '/pid/download_help',
                'target': 'new',
            }


    def search(self, cr, uid, domain, *args, **kwargs):
        # В журнале у пользователя должны отображаться только отчёты его предприятия и дочерних
        dep_ids = self.pool['eco.department'].search(cr, uid, [])
        domain += [('creator_department_id', 'in', dep_ids)]
        res = super(Pid, self).search(cr, uid, domain, *args, **kwargs)
        return res


    ##############################################################################################################
    #
    #  О знаках вопроса
    #
    ##############################################################################################################
    question_mark_block_button1 = fields.Html(default=help_mark, compute="_compute_question_mark",
        help=u"Внимание! Нажав кнопку «Заблокировать» Вы подтверждаете в достоверности внесенных сведений в данную карточку. Разблокировать карточку сможет руководитель структурного подразделения под свою ответственность")
    question_mark_block_button2 = fields.Html(default=help_mark, compute="_compute_question_mark",
        help=u"Внимание! Нажав кнопку «Заблокировать» Вы подтверждаете в достоверности внесенных сведений в данную карточку. Разблокировать карточку сможет руководитель структурного подразделения под свою ответственность")
    question_mark_block_button3 = fields.Html(default=help_mark, compute="_compute_question_mark",
        help=u"Внимание! Нажав кнопку «Заблокировать» Вы подтверждаете в достоверности внесенных сведений в данную карточку. Разблокировать карточку сможет руководитель структурного подразделения под свою ответственность")
    question_mark_block_button4 = fields.Html(default=help_mark, compute="_compute_question_mark",
        help=u"Внимание! Нажав кнопку «Заблокировать» Вы подтверждаете в достоверности внесенных сведений в данную карточку. Разблокировать карточку сможет руководитель структурного подразделения под свою ответственность")
    question_mark_akt_has_narush = fields.Html(default=help_mark, compute="_compute_question_mark",
        help=u"В случае выявленных нарушений и указанных в акте нажмите на ячейку с  флагом «Есть нарушения» после чего Вам откроется карточка для внесения сведений по нарушениям")
    question_mark_protokol = fields.Html(default=help_mark, compute="_compute_question_mark",
        help=u"Для продолжения внесения первичных сведений необходимо обязательно загрузить отсканированный протокол")
    question_mark_predpisanie = fields.Html(default=help_mark, compute="_compute_question_mark",
        help=u"Для продолжения внесения первичных сведений необходимо обязательно загрузить отсканированное предписание")
    question_mark_predpisanie_summa = fields.Html(default=help_mark, compute="_compute_question_mark",
        help=u"Внимание! Данная сумма будет автоматически импортирована в раздел ЗО-1 как факт оплаченного штрафа")

    @api.multi
    def _compute_question_mark(self):
        for rec in self:
            rec.question_mark_block_button1 = help_mark
            rec.question_mark_block_button2 = help_mark
            rec.question_mark_block_button3 = help_mark
            rec.question_mark_block_button4 = help_mark
            rec.question_mark_akt_has_narush = help_mark
            rec.question_mark_protokol = help_mark
            rec.question_mark_predpisanie = help_mark
            rec.question_mark_predpisanie_summa = help_mark


    ##############################################################################################################
    #
    #  Переменные вкладки "1. Основные сведения" представления' модуля eco.pret_isk'
    #
    ##############################################################################################################
    v1_01_changed = fields.Boolean()
    v1_01_with_sum1 = fields.One2many(related="v1_01")
    v1_01_with_sum2 = fields.One2many(related="v1_01")
    @api.onchange('v1_01')
    def _onchange_v1_01(self):
        self.v1_01_changed = True

    @api.multi
    def write(self, new_vals):
        if new_vals.get('v1_01_changed'):
            new_vals.pop('v1_01_with_sum1', None)
            new_vals.pop('v1_01_with_sum2', None)
        new_vals['v1_01_changed'] = False
        return super(Pid, self).write(new_vals)
    
    @api.model
    def create(self, vals):
        vals.pop('v1_01_with_sum1', None)
        vals.pop('v1_01_with_sum2', None)
        vals['v1_01_changed'] = False
        return super(Pid, self).create(vals)

    v1_01 = fields.One2many(
        'eco.pret_isk.pred_poligon',
        'pid_id',
        string=u"Предприятия и их полигоны", required=True,
    )
    v1_02 = fields.Text(u'Основание проведения проверки', required=True, default = u' ')
    v1_03 = fields.Selection([("plan_doc", u"Плановая документарная"), ("plan_out", u"Плановая выездная"),
        ("out_plan_doc", u"Внеплановая документарная"), ("out_plan_out", u"Внеплановая выездная")], string=u'Вид проверки', default="plan_doc")
    v1_04 = fields.Char(u"Исходящий номер", required=True, default = ' ')
    v1_05 = fields.Char(u"Номер входящего", required=True, default = ' ')
    v1_07 = fields.Text(u'Краткое содержание документа', required=True, default = ' ')
    v1_06 = fields.Date(u'Дата поступления в ОАО "РЖД"', required=True, default=lambda self: datetime.now())
    v1_08 = fields.Selection(_v1_08_SELECTION, string=u'ФОИВ осуществляющий проверку', default=_v1_08_NADZ[0][0])
    v1_09 = fields.Selection([("pric", u"Приказ"), ("rasp", u"Распоряжение"),], string=u'Наименования документа ', default="pric")
    v1_10 = fields.Date(u'Плановый срок исполнения', required=True, default=lambda self: datetime.now())
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
    protokol_zakon = fields.Selection([
        ('koap', u'КОаП РФ'),
        ('obl', u'Кодекс Московской области об административных правонарушениях'),
        ('msk', u'Кодекс г. Москвы об административных правонарушениях'),
        ('other', u'Иное законодательство')
        ], default="koap")
    protokol_iskodex_statia_id = fields.Many2one('eco.pret_isk.statia', u"Статья")
    protokol_iskodex_statia_kind = fields.Selection([
            ('1', u'Нарушения в области санитарного законодательства'),
            ('2', u'Нарушения законодательства в области охраны окружающей среды'),
                            ],
            default="1",
            string=u"Тип статьи")
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

    @api.onchange('protokol_iskodex_statia_id')
    def _onchange_protokol_iskodex_statia_id(self):
        self.protokol_description = self.protokol_iskodex_statia_id.name
        self.protokol_iskodex_statia_kind = self.protokol_iskodex_statia_id.kind
        self.protokol_iskodex_1 = self.protokol_iskodex_statia_id.nomer
        self.protokol_iskodex_2 = self.protokol_iskodex_statia_id.chast
        self.protokol_iskodex_3 = self.protokol_iskodex_statia_id.punkt
        self.protokol_iskodex_4 = self.protokol_iskodex_statia_id.ppunkt

    @api.onchange('protokol_zakon', 'act_problematica')
    def _onchange_protokol_zakon(self):
        self.protokol_iskodex_statia_id = False
        self.protokol_description = ""
        self.protokol_iskodex_1 = 0
        self.protokol_iskodex_2 = 0
        self.protokol_iskodex_3 = 0
        self.protokol_iskodex_4 = 0

    
    ##############################################################################################################
    #
    #  Переменные вкладки "4. Постановление' модуля eco.pret_isk'
    #
    ##############################################################################################################
    postanovlenie_file = fields.Binary(u"Предписание")
    postanovlenie_filename = fields.Char(u"Предписание")
    postanovlenie_description = fields.Text(u"Краткая суть")
    postanovlenie_date = fields.Date(u"Дата")
    #postanovlenie_zakon = fields.Selection([('1', u'КОаП РФ'), ('2', u'Иное законодательство'),], default="1")
    postanovlenie_zakon = fields.Selection([
        ('koap', u'КОаП РФ'),
        ('obl', u'Кодекс Московской области об административных правонарушениях'),
        ('msk', u'Кодекс г. Москвы об административных правонарушениях'),
        ('other', u'Иное законодательство')
        ], default="koap")

    postanovlenie_iskodex_statia_id = fields.Many2one('eco.pret_isk.statia', u"Статья")
    postanovlenie_iskodex_statia_kind = fields.Selection([
            ('1', u'Нарушения в области санитарного законодательства'),
            ('2', u'Нарушения законодательства в области охраны окружающей среды'), ],
            default="1",
            string=u"Тип статьи")
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

    @api.onchange('postanovlenie_iskodex_statia_id')
    def _onchange_postanovlenie_iskodex_statia_id(self):
        self.postanovlenie_description = self.postanovlenie_iskodex_statia_id.name
        self.postanovlenie_iskodex_statia_kind = self.postanovlenie_iskodex_statia_id.kind
        self.postanovlenie_iskodex_1 = self.postanovlenie_iskodex_statia_id.nomer
        self.postanovlenie_iskodex_2 = self.postanovlenie_iskodex_statia_id.chast
        self.postanovlenie_iskodex_3 = self.postanovlenie_iskodex_statia_id.punkt
        self.postanovlenie_iskodex_4 = self.postanovlenie_iskodex_statia_id.ppunkt

    @api.onchange('postanovlenie_zakon', 'act_problematica')
    def _onchange_postanovlenie_zakon(self):
        self.postanovlenie_iskodex_statia_id = False
        self.postanovlenie_description = ""
        self.postanovlenie_iskodex_statia_kind = False
        self.postanovlenie_iskodex_1 = 0
        self.postanovlenie_iskodex_2 = 0
        self.postanovlenie_iskodex_3 = 0
        self.postanovlenie_iskodex_4 = 0

    @api.multi
    def get_pret_state(self):
        self.ensure_one()
        # if not (self.akt_file and self.protokol_file and self.postanovlenie_file):
        #     res = u"Принято"
        if self.postanovlenie_is_accepted == '1' and self.postanovlenie_file:
            res = u"Исполнение постановления"
        elif self.postanovlenie_is_accepted == '2' and self.postanovlenie_file:
            res = u"Отмена постановления"
        elif self.postanovlenie_is_accepted == '3' and self.postanovlenie_file:
            res = u"Выполнение постановления"
        elif self.protokol_is_accepted == '1' and self.protokol_file:
            res = u"Исполнение протокола"
        elif self.protokol_is_accepted == '2' and self.protokol_file:
            res = u"Отмена протокола"
        elif self.protokol_is_accepted == '3' and self.protokol_file:
            res = u"Выполнение протокола"
        elif not self.akt_has_narush:
            res = u"Не выявлено"
        elif self.akt_is_accepted == '1' and self.akt_file:
            res = u"Исполнение предписания"
        elif self.akt_is_accepted == '2' and self.akt_file:
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
                for d in range(1, 5):
                    setattr(rec, 'can_see_unlock_tab%d' % d, getattr(rec, 'tab%d_done' % d))
            else:
                for d in range(1, 5):
                    setattr(rec, 'can_see_unlock_tab%d' % d, False)

    ##############################################################################################################
    #
    #  Экспорт текущей формы
    #
    ##############################################################################################################
    @api.multi
    def do_print_xlsx(self, workbook):
        raise exceptions.Warning(u"Находится в доработке")
        worksheet = workbook.add_worksheet(u'Штрафы')
        worksheet.set_column(0, tab1_width - 1, cell_width)
        r = tab1_str(workbook, worksheet, 0, u'Информация о предъявленных административных штрафах юридическим лицам')
        r, col_widths = table_1_head(workbook, worksheet, r)
        r = table_1_body(workbook, worksheet, r, get_report_data_from_record(self), col_widths)


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


class PredPoligon(models.Model):
    _description=u'Предприятие с его полигонами и суммой, взыскаемой с него'
    _name='eco.pret_isk.pred_poligon'
    _rec_name='department_id'

    pid_id = fields.Many2one('eco.pret_isk')

    department_id = fields.Many2one('eco.department', u"Предприятие",
        default = lambda self: self.env.user.department_id,   # при создании нету self-а в текущем контексте
    )
    rel_railway_id = fields.Many2one(related="department_id.rel_railway_id", readonly=True)
    summa3 = fields.Float(u"Сумма", digits=(10,3))
    summa4 = fields.Float(u"Сумма", digits=(10,3))


class Problem(models.Model):
    _name = 'eco.pret_isk.problems'
    _description = u'Проблематика ПИД'
    _rec_name = "problems_body"
    statia_ids = fields.One2many('eco.pret_isk.statia', 'problem_id', u"Статьи")

    name = fields.Char(u"name", default=u'Проблематика ПИД')
    problems_body = fields.Char(u"ПРОБЛЕМАТИКА", required=True)
    problems_category = fields.Integer(u"КАТЕГОРИЯ указана из Приложения № 2 (Анализ обращений граждан и надзорных органов)", required=True)


class Statia(models.Model):
    _name = 'eco.pret_isk.statia'
    _description = u'Статьи КОАП, законов Москвы и МО'
    problem_id = fields.Many2one('eco.pret_isk.problems')

    name = fields.Char(u"Наименование статьи")
    nomer = fields.Integer(u"Ст. №", default=0)
    chast = fields.Integer(u"ч. №", default=0)
    punkt = fields.Integer(u"п. №", default=0)
    ppunkt = fields.Integer(u"пп. №", default=0)
    zakon = fields.Char(u"Закон")
    kind = fields.Selection([
            ('1', u'Нарушения в области санитарного законодательства'),
            ('2', u'Нарушения законодательства в области охраны окружающей среды'), ],
            default="1",
            string=u"Тип статьи")
