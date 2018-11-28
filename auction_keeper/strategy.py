# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2018 reverendus, bargst
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import Optional, Tuple

from web3 import Web3

from auction_keeper.model import Status

from pymaker import Transact, Wad
from pymaker.approval import directly, hope_directly
from pymaker.auctions import Flopper, Flapper, Flipper


def era(web3: Web3):
    return web3.eth.getBlock('latest')['timestamp']


class Strategy:
    def approve(self):
        raise NotImplementedError

    def get_input(self, id: int):
        raise NotImplementedError


class FlipperStrategy(Strategy):
    def __init__(self, flipper: Flipper):
        assert isinstance(flipper, Flipper)

        self.flipper = flipper
        self.beg = flipper.beg()

    def approve(self):
        self.flipper.approve(hope_directly())

    def kicks(self) -> int:
        return self.flipper.kicks()

    def get_input(self, id: int) -> Status:
        assert isinstance(id, int)

        # Read auction state
        bid = self.flipper.bids(id)

        # Prepare the model input from auction state
        return Status(id=id,
                      flipper=self.flipper.address,
                      flapper=None,
                      flopper=None,
                      bid=bid.bid,
                      lot=bid.lot,
                      tab=bid.tab,
                      beg=self.beg,
                      guy=bid.guy,
                      era=era(self.flipper.web3),
                      tic=bid.tic,
                      end=bid.end,
                      price=(bid.bid / bid.lot) if bid.lot != Wad(0) else None)

    def bid(self, id: int, price: Wad) -> Tuple[Optional[Wad], Optional[Transact]]:
        assert isinstance(id, int)
        assert isinstance(price, Wad)

        bid = self.flipper.bids(id)

        # dent phase
        if bid.bid == bid.tab:
            our_lot = bid.bid / price

            if (our_lot * self.beg <= bid.lot) and (our_lot < bid.lot):
                return price, self.flipper.dent(id, our_lot, bid.bid)

            else:
                return None, None

        # tend phase
        else:
            our_bid = Wad.min(bid.lot * price, bid.tab)
            our_price = price if our_bid < bid.tab else bid.bid / bid.lot

            if (our_bid >= bid.bid * self.beg or our_bid == bid.tab) and our_bid > bid.bid:
                return our_price, self.flipper.tend(id, bid.lot, our_bid)

            else:
                return None, None

    def deal(self, id: int) -> Transact:
        return self.flipper.deal(id)


class FlapperStrategy(Strategy):
    def __init__(self, flapper: Flapper):
        assert isinstance(flapper, Flapper)

        self.flapper = flapper
        self.beg = flapper.beg()

    def approve(self):
        self.flapper.approve(directly())

    def kicks(self) -> int:
        return self.flapper.kicks()

    def get_input(self, id: int) -> Status:
        assert isinstance(id, int)

        # Read auction state
        bid = self.flapper.bids(id)

        # Prepare the model input from auction state
        return Status(id=id,
                      flipper=None,
                      flapper=self.flapper.address,
                      flopper=None,
                      bid=bid.bid,
                      lot=bid.lot,
                      tab=None,
                      beg=self.beg,
                      guy=bid.guy,
                      era=era(self.flapper.web3),
                      tic=bid.tic,
                      end=bid.end,
                      price=(bid.lot / bid.bid) if bid.bid != Wad(0) else None)

    def bid(self, id: int, price: Wad) -> Tuple[Optional[Wad], Optional[Transact]]:
        assert isinstance(id, int)
        assert isinstance(price, Wad)

        bid = self.flapper.bids(id)
        our_bid = bid.lot / price

        if our_bid >= bid.bid * self.beg and our_bid > bid.bid:
            return price, self.flapper.tend(id, bid.lot, our_bid)

        else:
            return None, None

    def deal(self, id: int) -> Transact:
        return self.flapper.deal(id)


class FlopperStrategy(Strategy):
    def __init__(self, flopper: Flopper):
        assert isinstance(flopper, Flopper)

        self.flopper = flopper
        self.beg = flopper.beg()

    def approve(self):
        self.flopper.approve(hope_directly())

    def kicks(self) -> int:
        return self.flopper.kicks()

    def get_input(self, id: int) -> Status:
        assert isinstance(id, int)

        # Read auction state
        bid = self.flopper.bids(id)

        # Prepare the model input from auction state
        return Status(id=id,
                      flipper=None,
                      flapper=None,
                      flopper=self.flopper.address,
                      bid=bid.bid,
                      lot=bid.lot,
                      tab=None,
                      beg=self.beg,
                      guy=bid.guy,
                      era=era(self.flopper.web3),
                      tic=bid.tic,
                      end=bid.end,
                      price=(bid.bid / bid.lot) if bid.lot != Wad(0) else None)

    def bid(self, id: int, price: Wad) -> Tuple[Optional[Wad], Optional[Transact]]:
        assert isinstance(id, int)
        assert isinstance(price, Wad)

        bid = self.flopper.bids(id)
        our_lot = bid.bid / price

        if our_lot * self.beg <= bid.lot and our_lot < bid.lot:
            return price, self.flopper.dent(id, our_lot, bid.bid)

        else:
            return None, None

    def deal(self, id: int) -> Transact:
        return self.flopper.deal(id)
