# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from . import party

__all__ = ['Bank', 'BankAccount']


class Bank(party.PartyCompanyMixin, metaclass=PoolMeta):
    __name__ = "bank"


class BankAccount(metaclass=PoolMeta):
    __name__ = 'bank.account'
    companies = fields.Function(fields.One2Many('company.company', None,
        'Companies'), 'get_companies', searcher='search_companies')

    def get_companies(self, name):
        if self.bank:
            return [c.id for c in self.bank.party.companies]

    @classmethod
    def search_companies(cls, name, clause):
        return [('bank.party.companies',) + tuple(clause[1:])]
