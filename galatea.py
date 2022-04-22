# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.transaction import Transaction

__all__ = ['GalateaUser']


class GalateaUser(metaclass=PoolMeta):
    __name__ = 'galatea.user'


    @classmethod
    def read(cls, ids, fields_names=None):
        # Skip access rule
        with Transaction().set_user(0):
            return super(GalateaUser, cls).read(ids, fields_names=fields_names)
