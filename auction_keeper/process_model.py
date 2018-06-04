# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2018 reverendus
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

from typing import Optional

from auction_keeper.model import ModelFactory, Model, ModelParameters, ModelInput, ModelOutput
from auction_keeper.process import Process


class ProcessModel(Model):
    def __init__(self, command: str):
        assert(isinstance(command, str))

        self.command = command
        self.process = None

    def start(self, parameters: ModelParameters):
        assert(self.process is None)

        arguments = f"{self.command} --id {parameters.id}"

        if parameters.flipper is not None:
            arguments += f" --flipper {parameters.flipper}"

        if parameters.flapper is not None:
            arguments += f" --flapper {parameters.flapper}"

        if parameters.flopper is not None:
            arguments += f" --flopper {parameters.flopper}"

        self.process = Process(self.command + " " + arguments)
        self.process.start()

    def input(self, input: ModelInput):
        assert(self.process is not None)

        #TODO
        pass

    def output(self) -> Optional[ModelOutput]:
        assert(self.process is not None)

        pass

    def stop(self):
        assert(self.process is not None)

        self.process.stop()


class ProcessModelFactory(ModelFactory):
    def __init__(self, command: str):
        assert(isinstance(command, str))

        self.command = command

    def create_model(self) -> Model:
        return ProcessModel(self.command)