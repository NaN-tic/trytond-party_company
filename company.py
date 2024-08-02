# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction


class Company(metaclass=PoolMeta):
    __name__ = 'company.company'

    allowed_party = fields.Function(fields.Boolean('Allowed Party'),
        'get_allowed_party', searcher='search_allowed_party')

    def get_allowed_party(self, name):
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)

        if self.party and user.company in self.party.companies:
            return True
        return False

    @classmethod
    def search_allowed_party(cls, name, clause):
        pool = Pool()
        PartyCompany = pool.get('party.company.rel')
        User = pool.get('res.user')
        Company = pool.get('company.company')

        party_company_table = PartyCompany.__table__()
        company_table = Company.__table__()

        user = User(Transaction().user)
        company = user.company or Company(
            Transaction().context.get('company', None))
        if not company:
            return []

        companies = company_table.join(party_company_table,
            condition=party_company_table.party==company_table.party).select(
            company_table.id,
            where=party_company_table.company==company.id)
        if clause[1] == '=':
            return ('id', 'in', companies)
        elif clause[1] == '!=':
            return ('id', 'not in', companies)
        return []
