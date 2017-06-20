# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields, ModelView, ModelSQL
from trytond.pool import PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import If, Eval

__all__ = ['Party', 'Address', 'PartyIdentifier', 'ContactMechanism']


class Party:
    __name__ = 'party.party'
    __metaclass__ = PoolMeta
    company = fields.Many2One('company.company', 'Company',
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ],
        select=True)

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class PartyCompanyMixin:
    company = fields.Function(fields.Many2One('company.company', 'Company'),
        'get_company', searcher='search_company')

    def get_company(self, name):
        return self.party.company.id if self.party.company else None

    @classmethod
    def search_company(cls, name, clause):
        return [('party.company',) + tuple(clause[1:])]


class Address(ModelSQL, ModelView, PartyCompanyMixin):
    __name__ = 'party.address'


class PartyIdentifier(ModelSQL, ModelView, PartyCompanyMixin):
    __name__ = 'party.identifier'


class ContactMechanism(ModelSQL, ModelView, PartyCompanyMixin):
    __name__ = 'party.contact_mechanism'
