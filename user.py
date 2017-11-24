# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['User']


class User:
    __metaclass__ = PoolMeta
    __name__ = 'res.user'

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        if not 'companies' in cls._context_fields:
            cls._context_fields.insert(0, 'companies')
