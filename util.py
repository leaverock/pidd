# -*- coding: utf-8 -*-
import logging

#log = {'__init__':False, '__openerp__':False, 'models':False, 'controllers':True, }
log = {'__init__':False, '__openerp__':False, 'models':False, 'controllers':False, }
log_name = u'c:/work/odoo/addons/pid/log.txt'

_logger = logging.getLogger(__name__)
def logInfo(name,val=False):
    if not val:
        _logger.info(unicode(name))
    else:
        _logger.info(unicode(name)+u'='+unicode(val))


def logFile(msg):
    with open( log_name, 'at') as f:
        f.write(msg + '\n')


def class_info(msg="", obj=None):
    with open(log_name, 'wt') as f:
        f.write(msg + '\n')
        for attr in dir(obj):
            if not attr.startswith('_'):
                try:
                    call = callable(getattr(obj,attr))
                except Exception as e:
                    call = '?' + str(e)
                f.write('attr: %s, call: %r\n' % (attr, call))
