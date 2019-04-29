#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ForeignExchange.ForeignExchange as FE_Module


def go_foreign_exchange():
    fe_paths = FE_Module.ForeignExchange.load_json("./ForeignExchange/foreign_exchange.json")
    tt_paths = FE_Module.TelegraphicTransfer.load_json("./ForeignExchange/telegraphic_transfer.json")
    c_paths = FE_Module.CompletePath(fe_paths, tt_paths)
    sorted_c = c_paths.remit_all_with_ntd(70 * 10000)

    sorted_f = FE_Module.ForeignExchange.sort(fe_paths, 'bank_sell', reverse=False)
    print(1)  # break here


if __name__ == "__main__":
    go_foreign_exchange()
