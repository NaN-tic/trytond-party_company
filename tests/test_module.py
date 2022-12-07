
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from contextlib import contextmanager
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.modules.company.tests import CompanyTestMixin, create_company


@contextmanager
def set_company(company):
    pool = Pool()
    User = pool.get('res.user')
    User.write([User(Transaction().user)], {
            'companies': [('add', [company.id])],
            'company': company.id,
                })
    with Transaction().set_context(User.get_preferences(context_only=True)):
        yield


class PartyCompanyTestCase(CompanyTestMixin, ModuleTestCase):
    'Test PartyCompany module'
    module = 'party_company'
    extras = ['bank']

    @with_transaction()
    def test_party(self):
        'Create party'
        pool = Pool()
        Party = pool.get('party.party')

        party1, = Party.create([{
                    'name': 'Party 1',
                    }])
        self.assertTrue(party1.id)
        self.assertEqual(party1.companies, ())

    @with_transaction()
    def test_party_company(self):
        'Create party company'
        pool = Pool()
        Party = pool.get('party.party')
        Address = pool.get('party.address')
        User = pool.get('res.user')

        company = create_company()
        with set_company(company):
            party = Party()
            party.name = 'Party 2'
            party.companies = [company]
            party.save()
            self.assertTrue(party.id)
            self.assertEqual(len(party.companies), 1)
            address, = Address.create([{
                        'party': party.id,
                        'street': 'St sample, 15',
                        'city': 'City',
                        }])
            self.assertEqual(address.companies == (company,), True)

            address1, address2 = Address.search([])
            self.assertEqual(address1.companies, ())
            self.assertEqual(address2.companies == (company,), True)

            user = User(Transaction().user)
            self.assertEqual(len(user.companies) == 1, True)
            self.assertEqual(user.companies[0] == company, True)

        company2 = create_company()
        with set_company(company2):
            user = User(Transaction().user)
            self.assertEqual(len(user.companies) == 2, True)
            self.assertEqual(user.companies[1] == company2, True)


del ModuleTestCase
