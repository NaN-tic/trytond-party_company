# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.transaction import Transaction
from trytond import backend
from . import party


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


class BankAccountNumber(metaclass=PoolMeta):
    __name__ = 'bank.account.number'

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().connection.cursor()

        # since issue11198 fill or create bank from IBAN and enforce uniqueness
        # replace default sql_constrain (keep same name) that always return false
        exist = backend.TableHandler.table_exist(cls._table)
        if exist:
            cursor.execute("ALTER TABLE bank_account_number DROP CONSTRAINT "
                "IF EXISTS bank_account_number_number_iban_exclude")
            cursor.execute("ALTER table bank_account_number add constraint "
                "bank_account_number_number_iban_exclude check (type != 'x')")

        super(BankAccountNumber, cls).__register__(module_name)
