#!/usr/bin/env python
# -*- coding: utf-8 -*-
from JsonAccessor.JsonAccessor import load_json


class SelfJsonLoader(object):
    @classmethod
    def load_json(cls, path):
        content = load_json(path)
        assert content['columns'] == cls.columns()
        return [cls(*datum) for datum in content['data']]

    @classmethod
    def columns(cls):
        raise NotImplementedError

    def __init__(self, *args):
        for attr, value in zip(self.columns(), args):
            self.__setattr__(attr, value)


class ForeignExchanger(SelfJsonLoader):
    @classmethod
    def columns(cls):
        return ['title', 'bank', 'date', 'bank_sell', 'bank_buy']

    @property
    def diff(self):
        return self.__getattribute__('bank_sell') - self.__getattribute__('bank_buy')

    @property
    def diff_ratio(self):
        return self.diff / self.__getattribute__('bank_sell')
