
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from contextlib import contextmanager
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.transaction import Transaction
from trytond.pool import Pool, isregisteredby
from trytond.modules.company.tests import CompanyTestMixin, create_company
from trytond.modules.company.model import CompanyMultiValueMixin


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


class PartyCompanyTestMixin(CompanyTestMixin):

    @property
    def _skip_company_rule(self):
        return super()._skip_company_rule | {
            ('party.configuration', 'company'),
            ('party.configuration-company', 'company'),
            }

    @with_transaction()
    def test_company_multivalue_context(self):
        "Test context of company multivalue target"
        pool = Pool()
        Company = pool.get('company.company')
        for mname, model in pool.iterobject():
            # skip rule user company in party.configuration
            if model.__name__ in ('party.configuration', 'party.configuration-company'):
                continue

            if (not isregisteredby(model, self.module)
                    or issubclass(model, Company)):
                continue
            company = None
            for fname, field in model._fields.items():
                if (field._type == 'many2one'
                        and issubclass(field.get_target(), Company)):
                    company = fname
                    break
            else:
                continue
            for fname, field in model._fields.items():
                if not hasattr(field, 'get_target'):
                    continue
                Target = field.get_target()
                if not issubclass(Target, CompanyMultiValueMixin):
                    continue
                if company in model._fields:
                    self.assertIn(
                        'company', list(field.context.keys()),
                        msg="Missing '%s' value as company "
                        'in "%s"."%s" context' % (
                            company, mname, fname))


class PartyCompanyTestCase(PartyCompanyTestMixin, ModuleTestCase):
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

            party = Party()
            party.name = 'Party 2'
            party.companies = [company, company2]
            party.save()
            self.assertEqual(len(party.companies), 2)

            # when copy party, set current company; default_company()
            new_party, = Party.copy([party])
            self.assertEqual(len(new_party.companies), 1)

del ModuleTestCase
