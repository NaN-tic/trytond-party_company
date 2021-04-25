# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from . import party


class Carrier(party.PartyCompanyMixin, metaclass=PoolMeta):
    __name__ = 'carrier'
