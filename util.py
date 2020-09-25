# -*- coding: utf-8 -*-
import logging

log = {'__init__':False, '__openerp__':False, 'models':False, 'controllers':True, }

_logger = logging.getLogger(__name__)
def logInfo(name,val=False):
    if not val:
        _logger.info(unicode(name))
    else:
        _logger.info(unicode(name)+u'='+unicode(val))


def logFile(msg):
    with open( u'c:/work/odoo/addons/pid/log.txt', 'at') as f:
        f.write(msg + '\n')




