# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, dualmethod
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['Cron']


class Cron(metaclass=PoolMeta):
    __name__ = "ir.cron"

    @dualmethod
    @ModelView.button
    def run_once(cls, crons):
        # overwrite run_once method because main_company is deprecated
        User = Pool().get('res.user')
        for cron in crons:
            if not cron.companies:
                super(Cron, cls).run_once([cron])
            else:
                # TODO replace with context
                for company in cron.companies:
                    User.write([cron.user], {
                            'company': company.id,
                            })
                    with Transaction().set_context(company=company.id):
                        super(Cron, cls).run_once([cron])
                User.write([cron.user], {
                        'company': None,
                        })
