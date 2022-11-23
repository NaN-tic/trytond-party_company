======================
Party Company Scenario
======================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard, Report
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.currency.tests.tools import get_currency
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.exceptions import UserWarning
    >>> today = datetime.date.today()

Install party_company::

    >>> config = activate_modules('party_company')

Create companies and currencies::

    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> Currency = Model.get('currency.currency')
    >>> User = Model.get('res.user')

    >>> euro = get_currency(code='EUR')
    >>> peso_colombian = get_currency(code='COP')

    >>> root, =  User.find([('active', '=', False), ('login', '=', 'root')])
    >>> config.user = root.id

    >>> party1 = Party(name='Company 1')
    >>> party1.save()
    >>> party2 = Party(name='Company 2')
    >>> party2.save()
    >>> party3 = Party(name='Company 3')
    >>> party3.save()

    >>> admin, = User.find([('login', '=', 'admin')])
    >>> config.user = admin.id
    >>> config._context = User.get_preferences(True, config.context)

    >>> _ = create_company(party=party1, currency=euro)
    >>> _ = create_company(party=party2, currency=euro)
    >>> _ = create_company(party=party3, currency=peso_colombian)

    >>> company1, company2, company3 = Company.find([])
    >>> admin.companies.append(company2)
    >>> admin.companies.append(company3)
    >>> admin.save()
    >>> config._context = User.get_preferences(True, config.context)

Create new users::

    >>> company2_user = User(User.copy([admin.id], config.context)[0])
    >>> company2_user.login = 'demo2'
    >>> company2_user.company = company2
    >>> company2_user.save()

Create new parties::

    >>> party4 = Party(name='Party 4')
    >>> party4.save()
    >>> len(party4.companies) == 1
    True
    >>> party4.companies[0] == admin.company
    True

    >>> config.user = company2_user.id
    >>> config._context = User.get_preferences(True, config.context)

    >>> party5 = Party(name='Party 5')
    >>> party5.save()
    >>> len(party5.companies) == 1
    True
    >>> party5.companies[0] == company2_user.company
    True

Delete companies in parties::

    >>> party6 = Party()
    >>> len(party6.companies) == 1
    True
    >>> company, = party6.companies
    >>> party6.companies.remove(company)
    >>> len(party6.companies) == 0
    True
    >>> party6.save()
    >>> len(party6.companies) == 0
    True
