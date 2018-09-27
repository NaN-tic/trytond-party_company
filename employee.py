# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.pyson import Eval, If
from trytond.transaction import Transaction

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
    def read(cls, ids, fields_names=None):
        # Skip access rule
        with Transaction().set_user(0):
            return super(Employee, cls).read(ids, fields_names=fields_names)
