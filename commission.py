# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from . import party

__all__ = ['Manager', 'Agent']


class Manager:
    __metaclass__ = PoolMeta
    __name__ = 'commission.manager'
    companies = fields.Function(fields.One2Many('company.company', None,
        'Companies'), 'get_companies', searcher='search_companies')

    def get_companies(self, name):
        if self.agent:
            return [c.id for c in self.agent.party.companies]

    @classmethod
    def search_companies(cls, name, clause):
        return [('agent.party.companies',) + tuple(clause[1:])]


class Agent(party.PartyCompanyMixin):
    __metaclass__ = PoolMeta
    __name__ = 'commission.agent'
