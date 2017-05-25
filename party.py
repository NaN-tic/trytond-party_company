# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import If, Eval
from trytond import backend

__all__ = ['Party', 'Address', 'PartyIdentifier', 'ContactMechanism']


class Party:
    __name__ = 'party.party'
    __metaclass__ = PoolMeta
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ],
        select=True)

    @classmethod
    def __register__(cls, module_name):
        Company = Pool().get('company.company')
        TableHandler = backend.get('TableHandler')
        sql_table = cls.__table__()
        table = TableHandler(cls, module_name)

        company_column = table.column_exist('company')

        super(Party, cls).__register__(module_name)
        if not company_column:
            companies = Company.search([], limit=1)
            if companies:
                company, = companies
                cursor = Transaction().connection.cursor()
                cursor.execute(*sql_table.update(
                        columns=[sql_table.company],
                        values=[company.id]))

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class Address:
    __name__ = 'party.address'
    __metaclass__ = PoolMeta
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ],
        select=True)

    @classmethod
    def __register__(cls, module_name):
        Company = Pool().get('company.company')
        TableHandler = backend.get('TableHandler')
        sql_table = cls.__table__()
        table = TableHandler(cls, module_name)

        company_column = table.column_exist('company')

        super(Address, cls).__register__(module_name)
        if not company_column:
            companies = Company.search([], limit=1)
            if companies:
                company, = companies
                cursor = Transaction().connection.cursor()
                cursor.execute(*sql_table.update(
                        columns=[sql_table.company],
                        values=[company.id]))

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class PartyIdentifier:
    __name__ = 'party.identifier'
    __metaclass__ = PoolMeta
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ],
        select=True)

    @classmethod
    def __register__(cls, module_name):
        Company = Pool().get('company.company')
        TableHandler = backend.get('TableHandler')
        sql_table = cls.__table__()
        table = TableHandler(cls, module_name)

        company_column = table.column_exist('company')

        super(PartyIdentifier, cls).__register__(module_name)
        if not company_column:
            companies = Company.search([], limit=1)
            if companies:
                company, = companies
                cursor = Transaction().connection.cursor()
                cursor.execute(*sql_table.update(
                        columns=[sql_table.company],
                        values=[company.id]))

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class ContactMechanism:
    __name__ = 'party.contact_mechanism'
    __metaclass__ = PoolMeta
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ],
        select=True)

    @classmethod
    def __register__(cls, module_name):
        Company = Pool().get('company.company')
        TableHandler = backend.get('TableHandler')
        sql_table = cls.__table__()
        table = TableHandler(cls, module_name)

        company_column = table.column_exist('company')

        super(ContactMechanism, cls).__register__(module_name)
        if not company_column:
            companies = Company.search([], limit=1)
            if companies:
                company, = companies
                cursor = Transaction().connection.cursor()
                cursor.execute(*sql_table.update(
                        columns=[sql_table.company],
                        values=[company.id]))

    @staticmethod
    def default_company():
        return Transaction().context.get('company')
