# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
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
