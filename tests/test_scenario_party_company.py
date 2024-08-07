import unittest

from proteus import Model
from trytond.modules.company.tests.tools import create_company
from trytond.modules.currency.tests.tools import get_currency
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install party_company
        config = activate_modules('party_company')

        # Create companies and currencies
        Company = Model.get('company.company')
        Party = Model.get('party.party')
        User = Model.get('res.user')
        euro = get_currency(code='EUR')
        peso_colombian = get_currency(code='COP')
        root, = User.find([('active', '=', False), ('login', '=', 'root')])
        config.user = root.id
        party1 = Party(name='Company 1')
        party1.save()
        party2 = Party(name='Company 2')
        party2.save()
        party3 = Party(name='Company 3')
        party3.save()
        admin, = User.find([('login', '=', 'admin')])
        config.user = admin.id
        config._context = User.get_preferences(True, config.context)
        _ = create_company(party=party1, currency=euro)
        _ = create_company(party=party2, currency=euro)
        _ = create_company(party=party3, currency=peso_colombian)
        company1, company2, company3 = Company.find([])
        admin.companies.append(company2)
        admin.companies.append(company3)
        admin.save()
        config._context = User.get_preferences(True, config.context)

        # Create new users
        company2_user = User(User.copy([admin.id], config.context)[0])
        company2_user.login = 'demo2'
        company2_user.company = company2
        company2_user.save()

        # Create new parties
        party4 = Party(name='Party 4')
        party4.save()
        self.assertEqual(len(party4.companies), 1)
        self.assertEqual(party4.companies[0], admin.company)
        config.user = company2_user.id
        config._context = User.get_preferences(True, config.context)
        party5 = Party(name='Party 5')
        party5.save()
        self.assertEqual(len(party5.companies), 1)
        self.assertEqual(party5.companies[0], company2_user.company)

        # Delete companies in parties
        party6 = Party()
        self.assertEqual(len(party6.companies), 1)
        company, = party6.companies
        party6.companies.remove(company)
        self.assertEqual(len(party6.companies), 0)
        party6.save()
        self.assertEqual(len(party6.companies), 0)
