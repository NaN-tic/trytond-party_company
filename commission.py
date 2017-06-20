# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from . import party

__all__ = ['Agent']


class Agent(party.PartyCompanyMixin):
    __name__ = 'commission.agent'
    __metaclass__ = PoolMeta
