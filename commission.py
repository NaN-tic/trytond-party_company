# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Agent']


class Agent:
    __name__ = 'commission.agent'
    __metaclass__ = PoolMeta
    company = fields.Function(fields.Many2One('company.company', 'Company'),
        'get_company', searcher='search_company_field')

    def get_company(self, name):
        if self.party and self.party.company:
            return self.party.company.id

    @classmethod
    def search_company_field(cls, name, clause):
        return [('party.company',) + tuple(clause[1:])]
