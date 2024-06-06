# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond import backend
from . import party


class Bank(party.PartyCompanyMixin, metaclass=PoolMeta):
    __name__ = "bank"


class BankAccount(metaclass=PoolMeta):
    __name__ = 'bank.account'
    companies = fields.Function(fields.One2Many('company.company', None,
        'Companies'), 'get_companies', searcher='search_companies')
    owners_by_companies = fields.Function(
        fields.Many2Many('bank.account-party.party', 'account', 'owner',
        'Owners'), 'get_owners_by_companies', setter='set_owners_by_companies')

    @classmethod
    def create(cls, vlist):
        # allow create bank accounts from party when not select owners
        with Transaction().set_context(_check_access=False):
            return super(BankAccount, cls).create(vlist)

    def get_companies(self, name):
        if self.bank:
            return [c.id for c in self.bank.party.companies]

    @classmethod
    def search_companies(cls, name, clause):
        return ['OR',
            ('bank', '=', None),
            ('bank.party.companies',) + tuple(clause[1:]),
            ]

    @classmethod
    def get_owners_by_companies(cls, records, name):
        PartyCompany = Pool().get('party.company.rel')

        user_company = Transaction().context.get('company')

        res = dict((x.id, None) for x in records)
        for record in records:
            owners = []

            for owner in record.owners:
                owner_companies = [o.company for o in PartyCompany.search([
                    ('party', '=', owner),
                    ])]
                if not owner_companies:
                    owners.append(owner)
                    continue
                for company in owner_companies:
                    if company.id == user_company:
                        owners.append(owner)
                        break
            res[record.id] = [o.id for o in owners]
        return res

    @classmethod
    def set_owners_by_companies(cls, records, name, value):
        cls.write(records, {'owners': value})


class BankAccountNumber(metaclass=PoolMeta):
    __name__ = 'bank.account.number'

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().connection.cursor()

        # since issue11198 fill or create bank from IBAN and enforce uniqueness
        # replace default sql_constrain (keep same name) that always return false
        exist = backend.TableHandler.table_exist(cls._table)
        if exist and backend.name == 'postgresql':
            cursor.execute("ALTER TABLE bank_account_number DROP CONSTRAINT "
                "IF EXISTS bank_account_number_number_iban_exclude")
            cursor.execute("ALTER TABLE bank_account_number DROP CONSTRAINT "
                "IF EXISTS bank_account_number_number_iban_active_exclude")
            cursor.execute("ALTER table bank_account_number add constraint "
                "bank_account_number_number_iban_active_exclude check (type != 'x')")

        super(BankAccountNumber, cls).__register__(module_name)
