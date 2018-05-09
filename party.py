# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from sql import Literal, Null
from sql.aggregate import Count
from trytond.model import ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond import backend

__all__ = ['PartyCompany', 'Party', 'Address', 'PartyIdentifier',
    'ContactMechanism']


class Party:
    __name__ = 'party.party'
    __metaclass__ = PoolMeta
    companies = fields.Function(fields.Many2Many('party.party-company.company',
        'party', 'company', 'Companies', domain=[
            ('id', 'in', Eval('context', {}).get('companies', [])),
        ]), 'get_companies',
        searcher='search_companies_field', setter='set_companies_field')

    @classmethod
    def __setup__(cls):
        super(Party, cls).__setup__()
        if hasattr(cls, 'agent'):
            agent_domain = [
                ('id', 'in', Eval('context', {}).get('companies', [])),
                ]
            if cls.agent.domain:
                agent_domain += cls.agent.domain
            # TODO upgrade 4.7 replace Property to MultiValue issue2349
            cls.agent = fields.Property(fields.Many2One('commission.agent',
                'Agent', domain=agent_domain))
        cls._error_messages.update({
                'can_not_remove_companies': ('Can not remove companies related '
                    'on parties.'),
                })

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        PartyCompany = pool.get('party.party-company.company')

        sql_table = cls.__table__()
        TableHandler = backend.get('TableHandler')

        super(Party, cls).__register__(module_name)

        transaction = Transaction()
        cursor = transaction.connection.cursor()
        table = TableHandler(cls, module_name)

        if (table.column_exist('company')):
            sql_where = (sql_table.company != Null)
            limit = transaction.database.IN_MAX
            cursor.execute(*sql_table.select(Count(Literal(1)), where=sql_where))
            party_count, = cursor.fetchone()
            party_companies = []
            for offset in range(0, party_count, limit):
                cursor.execute(*sql_table.select(
                        sql_table.id, sql_table.company,
                        where=sql_where,
                        order_by=sql_table.id,
                        limit=limit, offset=offset))
                for party_id, company_id in cursor.fetchall():
                    party_companies.append(
                        PartyCompany(party=party_id, company=company_id))
            if party_companies:
                PartyCompany.save(party_companies)
            table.drop_column('company')

    @staticmethod
    def default_companies():
        if Transaction().context.get('company'):
            return [Transaction().context.get('company')]
        return []

    @classmethod
    def copy(cls, parties, default=None):
        if default is None:
            default = {}
        default = default.copy()
        company_id = Transaction().context.get('company')
        if company_id:
            default['companies'] = [company_id]
        return super(Party, cls).copy(parties, default=default)

    @classmethod
    def delete(cls, parties):
        PartyCompany = Pool().get('party.party-company.company')

        party_company = PartyCompany.__table__()
        cursor = Transaction().connection.cursor()
        party_ids = [p.id for p in parties]

        super(Party, cls).delete(parties)

        cursor.execute(*party_company.delete(
            where=(party_company.party.in_(party_ids))
            ))

    @classmethod
    def get_companies(cls, parties, names):
        pool = Pool()
        PartyCompany = pool.get('party.party-company.company')
        User = pool.get('res.user')

        party_company = PartyCompany.__table__()

        cursor = Transaction().connection.cursor()
        party_ids = [p.id for p in parties]

        result = {}
        for name in names:
            result[name] = dict((p.id, []) for p in parties)

        user = User(Transaction().user)
        if not user.company:
            return result

        company_ids = [c.id for c in user.companies]

        for name in names:
            cursor.execute(*party_company.select(
                party_company.party, party_company.company,
                where=(party_company.party.in_(party_ids) &
                    party_company.company.in_(company_ids)))
                )
            for party, value in cursor.fetchall():
                result[name][party].append(value)
        return result

    @classmethod
    def search_companies_field(cls, name, clause):
        pool = Pool()
        Company = pool.get('company.company')
        PartyCompany = pool.get('party.party-company.company')
        Party = pool.get('party.party')
        User = pool.get('res.user')

        party_company = PartyCompany.__table__()
        party_h = Party.__table__()

        user = User(Transaction().user)
        if not user.company:
            return

        # return parties have not company
        if clause[2] == []:
            query = party_h.join(party_company,
                type_='LEFT',
                condition=party_h.id == party_company.party).select(
                    party_h.id,
                    where=party_company.party == Null)
            return [('id', 'in', query)]

        # return parties have a company
        if clause[1] == 'in':
            sql_where = party_company.company.in_(clause[2])
        elif clause[1] == 'not in':
            sql_where = ~party_company.company.in_(clause[2])
        else:
            companies = Company.search([
                ('party.name', clause[1], clause[2]),
                ])
            if clause[1] == 'ilike' or clause[1] == '=':
                sql_where = party_company.company.in_([c.id for c in companies])
            elif clause[1] == 'not ilike' or clause[1] == '!=':
                sql_where = ~party_company.company.in_([c.id for c in companies])
            else:
                return [('id', 'in', [])]
        query = party_company.select(party_company.party, where=(sql_where))
        return [('id', 'in', query)]

    @classmethod
    def set_companies_field(cls, parties, name, value):
        pool = Pool()
        PartyCompany = pool.get('party.party-company.company')

        party_company = PartyCompany.__table__()
        cursor = Transaction().connection.cursor()
        party_ids = [p.id for p in parties]

        # TODO support add and remove
        to_add = []
        to_remove = []
        for val in value:
            if val[0] == 'add':
                to_add = val[1]
            if val[0] == 'remove':
                to_remove = val[1]

        if to_add:
            # check that company in party is not current added
            cursor.execute(*party_company.select(
                party_company.party, party_company.company,
                where=(party_company.party.in_(party_ids) &
                    party_company.company.in_(to_add)))
                )
            pcs = {}
            for party, value in cursor.fetchall():
                if party in pcs:
                    pcs[party] += [value]
                else:
                    pcs[party] = [value]

            to_create = []
            for party in parties:
                party_id = party.id
                for company in to_add:
                    if party_id in pcs and company in pcs[party_id]:
                        continue
                    # new company, we add it
                    pc = PartyCompany()
                    pc.party = party
                    pc.company = company
                    to_create.append(pc._save_values)
            if to_create:
                PartyCompany.create(to_create)

        if to_remove:
            cls.raise_user_error('can_not_remove_companies')


class PartyCompanyMixin:
    companies = fields.Function(fields.One2Many('company.company', None,
        'Companies'), 'get_companies', searcher='search_companies')

    def get_companies(self, name):
        if self.party:
            return [c.id for c in self.party.companies]
        return []

    @classmethod
    def search_companies(cls, name, clause):
        return [('party.companies',) + tuple(clause[1:])]


class Address(object, PartyCompanyMixin):
    __metaclass__ = PoolMeta
    __name__ = 'party.address'


class PartyIdentifier(object, PartyCompanyMixin):
    __metaclass__ = PoolMeta
    __name__ = 'party.identifier'


class ContactMechanism(object, PartyCompanyMixin):
    __metaclass__ = PoolMeta
    __name__ = 'party.contact_mechanism'


class PartyCompany(ModelSQL):
    'Party - Company'
    __name__ = 'party.party-company.company'
    _table = 'party_company_rel'
    party = fields.Many2One('party.party', 'Party', ondelete='CASCADE',
            required=True, select=True)
    company = fields.Many2One('company.company', 'Company',
        ondelete='CASCADE', required=True, select=True)
