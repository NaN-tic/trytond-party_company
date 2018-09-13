# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, If

__all__ = ['Employee']

class Employee(metaclass=PoolMeta):
    __name__ = 'company.employee'

    @classmethod
    def __setup__(cls):
        super(Employee, cls).__setup__()
        cls.company.domain = [
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ]

    @classmethod
    def search(cls, args, offset=0, limit=None, order=None, count=False,
            query=False):
        Rule = Pool().get('ir.rule')
        # TODO clear domain cache because when an user change company (set preferences),
        # the new domain cache is [u'company', u'=', None] and not return
        # employees with company context. At the moment, search employees
        # drop domain cache (clear)
        Rule._domain_get_cache.clear()
        return super(Employee, cls).search(args, offset, limit, order,
            count, query)
