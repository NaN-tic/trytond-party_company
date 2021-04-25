# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, dualmethod
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction


class Cron(metaclass=PoolMeta):
    __name__ = "ir.cron"

    @dualmethod
    @ModelView.button
    def run_once(cls, crons):
        pool = Pool()
        User = pool.get('res.user')
        ModelData = pool.get('ir.model.data')

        user = User(ModelData.get_id('party_company', 'user_party_company'))

        for cron in crons:
            if not cron.companies:
                super(Cron, cls).run_once([cron])
            else:
                # TODO replace with context
                for company in cron.companies:
                    User.write([user], {
                            'company': company.id,
                            })
                    with Transaction().set_context(company=company.id):
                        super(Cron, cls).run_once([cron])
                User.write([user], {
                        'company': None,
                        })
