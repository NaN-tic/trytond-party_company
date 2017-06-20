# This file is part party_company module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.modules.company.tests import create_company, set_company


class PartyCompanyTestCase(ModuleTestCase):
    'Test Party Company module'
    module = 'party_company'

    @with_transaction()
    def test_party(self):
        'Create party'
        pool = Pool()
        Party = pool.get('party.party')

        party1, = Party.create([{
                    'name': 'Party 1',
                    }])
        self.assert_(party1.id)
        self.assertEqual(party1.company, None)

    @with_transaction()
    def test_party_company(self):
        'Create party company'
        pool = Pool()
        Party = pool.get('party.party')
        Address = pool.get('party.address')

        company = create_company()
        with set_company(company):
            party, = Party.create([{
                        'name': 'Party 2',
                        }])
            self.assert_(party.id)
            self.assertNotEqual(party.company, None)
            address, = Address.create([{
                        'party': party.id,
                        'street': 'St sample, 15',
                        'city': 'City',
                        }])
            self.assertEqual(address.company == company, True)

            address1, address2 = Address.search([])
            self.assertEqual(address1.company, None)
            self.assertEqual(address2.company == company, True)

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            PartyCompanyTestCase))
    return suite
