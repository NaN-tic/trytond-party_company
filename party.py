# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
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


class Address:
    __name__ = 'party.address'
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


class PartyIdentifier:
    __name__ = 'party.identifier'
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


class ContactMechanism:
    __name__ = 'party.contact_mechanism'
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
