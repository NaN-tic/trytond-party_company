# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from sql import Literal, Null
from sql.aggregate import Count
from trytond.model import ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond import backend
from trytond.i18n import gettext
from trytond.exceptions import UserError
from trytond.model.exceptions import AccessError


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    companies = fields.Function(fields.Many2Many('party.company.rel',
        'party', 'company', 'Companies', domain=[
            ('id', 'in', Eval('context', {}).get('companies', [])),
        ]), 'get_companies',
        searcher='search_companies_field', setter='set_companies_field')

    current_company = fields.Function(fields.Boolean('Current Company'),
        'get_current_company', searcher='search_current_company')

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        PartyCompany = pool.get('party.company.rel')

        sql_table = cls.__table__()

        super(Party, cls).__register__(module_name)

        transaction = Transaction()
        cursor = transaction.connection.cursor()
        table = backend.TableHandler(cls, module_name)

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

    @classmethod
    def default_companies(cls):
        Configuration = Pool().get('party.configuration')

        config = Configuration(1)
        company_ids = [c.id for c in config.default_companies]

        company_id = Transaction().context.get('company')
        if company_id and company_id > 0 and company_id not in company_ids:
            company_ids.append(company_id)
        return company_ids

    @classmethod
    def delete(cls, parties):
        PartyCompany = Pool().get('party.company.rel')

        party_company = PartyCompany.__table__()
        cursor = Transaction().connection.cursor()
        party_ids = [p.id for p in parties]

        super(Party, cls).delete(parties)

        if party_ids:
            cursor.execute(*party_company.delete(
                where=(party_company.party.in_(party_ids))
                ))

    def get_current_company(self, name):
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)

        # Return "True" if we have no companies or we have the same company as
        # user
        if not self.companies:
            return True

        for company in self.companies:
            if company == user.company:
                return True
        return False

    @classmethod
    def get_companies(cls, parties, names):
        pool = Pool()
        PartyCompany = pool.get('party.company.rel')
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
        if not company_ids:
            return result

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
    def search_current_company(cls, name, clause):
        pool = Pool()
        PartyCompany = pool.get('party.company.rel')
        User = pool.get('res.user')
        Company = pool.get('company.company')

        party_company = PartyCompany.__table__()

        user = User(Transaction().user)
        if not user.company:
            companies = Company.search([], limit=1)
            # If there are no companies yet, then allow access
            # to all parties
            if not companies:
                return []
            return [('id', '=', -1)]

        with_company = party_company.select(party_company.party,
            where=party_company.company==user.company.id)

        party_company2 = PartyCompany.__table__()
        without_company = party_company2.select(party_company2.party)

        parties = [x.party.id for x in user.companies]

        if clause[1] == '=':
            return ['OR',
                ('id', 'in', with_company),
                ('id', 'not in', without_company),
                ('id', 'in', parties),
                ]
        elif clause[1] == '!=':
            return [
                ('id', 'not in', with_company),
                ('id', 'in', without_company),
                ('id', 'not in', parties),
                ]
        return []

    @classmethod
    def search_companies_field(cls, name, clause):
        pool = Pool()
        Company = pool.get('company.company')
        PartyCompany = pool.get('party.company.rel')
        Party = pool.get('party.party')
        User = pool.get('res.user')

        party_company = PartyCompany.__table__()
        party_h = Party.__table__()

        user = User(Transaction().user)
        if not user.company:
            return []

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
            if companies and (clause[1] == 'ilike' or clause[1] == '='):
                sql_where = party_company.company.in_([c.id for c in companies])
            elif companies and (clause[1] == 'not ilike' or clause[1] == '!='):
                sql_where = ~party_company.company.in_([c.id for c in companies])
            else:
                return [('id', 'in', [])]
        query = party_company.select(party_company.party, where=(sql_where))
        return [('id', 'in', query)]

    @classmethod
    def set_companies_field(cls, parties, name, value):
        pool = Pool()
        PartyCompany = pool.get('party.company.rel')
        Data = pool.get('ir.model.data')

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
                    to_create.append(pc._save_values())
            if to_create:
                PartyCompany.create(to_create)

        if to_remove:
            groups = Transaction().context.get('groups', [])
            group_admin = Data.get_id('res', 'group_admin')
            if group_admin not in groups:
                raise UserError(gettext('party_company.can_not_remove_companies'))

            cls.check_remove_parties_by_company(parties, to_remove)

            to_delete = PartyCompany.search([
                ('party', 'in', parties),
                ('company', 'in', to_remove),
                ])
            PartyCompany.delete(to_delete)

    @classmethod
    def check_models_by_company(cls):
        return ('sale.sale', 'purchase.purchase', 'account.invoice',
            'account.move.line')

    @classmethod
    def check_remove_parties_by_company(cls, parties, companies):
        pool = Pool()
        Model = pool.get('ir.model')

        for model in cls.check_models_by_company():
            try:
                MModel = pool.get(model)
            except KeyError:
                continue

            with Transaction().set_context(_check_access=False):
                if MModel.search([
                        ('party', 'in', parties),
                        ('company', 'in', companies),
                        ]):
                    model, = Model.search([('name', '=', model)], limit=1)
                    raise AccessError(
                        gettext('party_company.msg_can_not_remove_model_companies',
                        model=model.rec_name))


class PartyCompanyMixin(object):
    __slots__ = ()
    companies = fields.Function(fields.One2Many('company.company', None,
        'Companies'), 'get_companies', searcher='search_companies')

    def get_companies(self, name):
        if self.party:
            return [c.id for c in self.party.companies]
        return []

    @classmethod
    def search_companies(cls, name, clause):
        return [('party.companies',) + tuple(clause[1:])]


class Address(PartyCompanyMixin, metaclass=PoolMeta):
    __name__ = 'party.address'


class PartyIdentifier(PartyCompanyMixin, metaclass=PoolMeta):
    __name__ = 'party.identifier'


class ContactMechanism(PartyCompanyMixin, metaclass=PoolMeta):
    __name__ = 'party.contact_mechanism'


class PartyCompany(ModelSQL):
    'Party - Company'
    __name__ = 'party.company.rel'
    _table = 'party_company_rel'
    party = fields.Many2One('party.party', 'Party', ondelete='CASCADE',
            required=True, context={
                'company': Eval('company', -1),
            }, depends=['company'])
    company = fields.Many2One('company.company', 'Company',
        ondelete='CASCADE', required=True)
