# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from . import party

__all__ = ['Carrier']


class Carrier(object, party.PartyCompanyMixin):
    __metaclass__ = PoolMeta
    __name__ = 'carrier'
