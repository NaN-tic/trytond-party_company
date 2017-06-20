# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from . import party

__all__ = ['Bank', 'BankAccount']


class Bank(object, party.PartyCompanyMixin):
    __metaclass__ = PoolMeta
    __name__ = "bank"


class BankAccount:
    __metaclass__ = PoolMeta
    __name__ = 'bank.account'
    company = fields.Function(fields.Many2One('company.company', 'Company'),
        'get_company', searcher='search_company_field')

    def get_company(self, name):
        if self.bank and self.bank.party.company:
            return self.bank.party.company.id

    @classmethod
    def search_company_field(cls, name, clause):
        return [('bank.party.company',) + tuple(clause[1:])]
