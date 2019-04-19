#!/usr/bin/env python
# -*- coding: utf-8 -*-
from JsonAccessor.JsonAccessor import load_json


class SelfJsonLoader(object):
    @classmethod
    def load_json(cls, path):
        content = load_json(path)
        assert content['columns'] == cls.columns()
        return [cls(columns) for columns in content['data']]

    @classmethod
    def columns(cls):
        raise NotImplementedError


class ForeignExchange(SelfJsonLoader):
    @classmethod
    def columns(cls):
        return ['title', 'bank', 'date', 'bank_sell', 'bank_buy', 'discount']

    @staticmethod
    def sort(fe_paths, attr, reverse=False):
        result = list(map(lambda path: (path.__getattribute__(attr), path), fe_paths))
        return sorted(result, key=lambda path: path[0], reverse=reverse)

    def __init__(self, columns):
        super().__init__()
        iterator = iter(columns)
        self.title = next(iterator)
        self.bank = next(iterator)
        self.date = next(iterator)
        self.bank_sell = next(iterator)
        self.bank_buy = next(iterator)
        discount = next(iterator)
        if isinstance(discount, float):
            self.bank_sell -= discount
            self.bank_buy += discount
        if self.bank_sell < self.bank_buy:
            raise ValueError

    @property
    def diff(self):
        return self.bank_sell - self.bank_buy

    @property
    def diff_ratio(self):
        return self.diff / self.bank_sell

    def buy(self, ntd):
        return ntd / self.bank_sell

    def sell(self, usd):
        return usd * self.bank_buy


class TelegraphicTransfer(SelfJsonLoader):
    ESTIMATED_TRANSSHIPMENT_USD = 20

    @classmethod
    def columns(cls):
        return ['title', 'bank', 'date', 'commission_rate', 'commission_min', 'commission_max', 'telegram', 'our']

    def __init__(self, columns):
        super().__init__()
        iterator = iter(columns)
        self.title = next(iterator)
        self.bank = next(iterator)
        self.date = next(iterator)
        self.commission_rate = next(iterator)
        self.commission_min = next(iterator)
        self.commission_max = next(iterator)
        self.telegram = next(iterator)
        self.our = next(iterator)

    def get_commission(self, ntd):
        commission = ntd * self.commission_rate
        if isinstance(self.commission_min, int):
            commission = max(commission, self.commission_min)
        if isinstance(self.commission_max, int):  # 允許 max < min 時作用
            commission = min(commission, self.commission_max)
        return commission

    def get_transshipment_cost(self, exchange_rate):
        """
        :return: cost, is_our
        """
        estimated = self.ESTIMATED_TRANSSHIPMENT_USD * exchange_rate
        if self.our and (self.our <= estimated):
            return self.our, True
        else:
            return estimated, False

    def remit_cost(self, ntd, exchange_rate):
        """
        :return: cost, is_our
        """
        commission = self.get_commission(ntd)
        transshipment_cost, is_our = self.get_transshipment_cost(exchange_rate)
        return commission + self.telegram + transshipment_cost, is_our


class CompletePath(object):
    @staticmethod
    def compose_paths(fe_paths, tt_paths):
        result = []
        for tt_path in tt_paths:
            result.extend((fe_path, tt_path) for fe_path in fe_paths if fe_path.bank == tt_path.bank)
        return result

    @staticmethod
    def remit_with_ntd(complete_path, ntd):
        fe_path = complete_path[0]
        tt_path = complete_path[1]

        cost, is_our = tt_path.remit_cost(ntd, fe_path.bank_sell)
        return {
            'fe': fe_path,
            'tt': tt_path,
            'result': fe_path.buy(ntd - cost),
            'cost': cost,
            'is_our': is_our
        }

    def __init__(self, fe_paths, tt_paths):
        super().__init__()
        self.path = self.compose_paths(fe_paths, tt_paths)

    def remit_all_with_ntd(self, ntd):
        result = list(map(lambda path: self.remit_with_ntd(path, ntd), self.path))
        return sorted(result, key=lambda res: res['result'], reverse=True)


def test_swap(paths):
    ntd = 77.5
    return [(path.buy(ntd), path) for path in paths]


def test_remit(paths):
    return [(path.remit_cost(77.5, 30.8), path.title) for path in paths]


if __name__ == "__main__":
    fe_paths = ForeignExchange.load_json("foreign_exchange.json")
    tt_paths = TelegraphicTransfer.load_json("telegraphic_transfer.json")
    c_paths = CompletePath(fe_paths, tt_paths)
    sorted_c = c_paths.remit_all_with_ntd(70 * 10000)

    sorted_f = ForeignExchange.sort(fe_paths, 'bank_sell', reverse=False)
    print(1)
