# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import copy
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelSQL, fields
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond import backend
from sql import Table, Null, Column
from sql.functions import CurrentTimestamp

__all__ = ['User', 'UserCompany']


class User(metaclass=PoolMeta):
    __name__ = 'res.user'
    main_companies = fields.Many2Many('res.user-company.company', 'user',
        'company', 'Main Companies')

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        if not 'companies' in cls._context_fields:
            cls._context_fields.insert(0, 'companies')

        # replace company field domain and depends
        domain = cls.company.domain
        new_domain = [d for d in domain if not 'main_company' in str(d)]
        new_domain.append(
            ('parent', 'child_of', Eval('main_companies'), 'parent'))
        cls.company.domain = new_domain
        depends = cls.company.depends
        depends.append('main_companies')
        if 'main_company' in depends:
            depends.remove('main_company')
        cls.company.depends = depends

    @classmethod
    def get_companies(cls, users, name):
        Company = Pool().get('company.company')

        companies = super(User, cls).get_companies(users, name)

        companies = {}
        company_childs = {}
        for user in users:
            companies[user.id] = []
            for company in user.main_companies:
                if company in company_childs:
                    company_ids = company_childs[company]
                else:
                    company_ids = list(map(int, Company.search([
                                ('parent', 'child_of', [company.id]),
                                ])))
                    company_childs[company] = company_ids
                if company_ids:
                    companies[user.id].extend(company_ids)
        return companies

    @classmethod
    def get_preferences_fields_view(cls):
        Company = Pool().get('company.company')

        res = super(User, cls).get_preferences_fields_view()
        res = copy.deepcopy(res)

        if 'company' in res['fields']:
            user = cls(Transaction().user)
            selection = [(None, '')]
            company_ids = [c.id for c in user.main_companies]
            if company_ids:
                companies = Company.search([
                        ('parent', 'child_of', company_ids,
                            'parent'),
                        ])
                for company in companies:
                    selection.append((company.id, company.rec_name))
            res['fields']['company']['selection'] = selection
        return res


class UserCompany(ModelSQL):
    'User - Company'
    __name__ = 'res.user-company.company'
    _table = 'res_user_company_rel'
    user = fields.Many2One('res.user', 'User', ondelete='CASCADE',
            required=True, select=True)
    company = fields.Many2One('company.company', 'Company',
        ondelete='CASCADE', required=True, select=True)

    @classmethod
    def __register__(cls, module_name):
        User = Pool().get('res.user')
        TableHandler = backend.get('TableHandler')
        user_company_table_name = 'res_user_company_rel'
        cursor = Transaction().connection.cursor()

        user_company_table_exist = False
        if TableHandler.table_exist(user_company_table_name):
            user_company_table_exist = True

        super(UserCompany, cls).__register__(module_name)

        if not user_company_table_exist:
            # update main_company to null
            user = User.__table__()
            query = user.update(
                    columns=[user.main_company],
                    values=[None],
                    where=user.main_company != Null)
            cursor.execute(*query)

            # insert company user
            fields = ['create_uid', 'create_date', 'user', 'company']
            query = user.select(user.id, user.company,
                where=(user.company != Null))
            cursor.execute(*query)
            values = [(0, CurrentTimestamp(), user_id, company_id) for user_id,
                company_id in cursor.fetchall()]
            if values:
                user_company = Table(user_company_table_name)
                query = user_company.insert(
                        columns=[Column(user_company, f) for f in fields],
                        values=values)
                cursor.execute(*query)
