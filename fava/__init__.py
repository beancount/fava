# -*- coding: utf-8 -*-
"""
    Fava – A web interface for beancount.
    Copyright ©  2015-2016 Dominik Aumayr <dominik@aumayr.name>
    Licensed under the MIT License.
    You may not use this file except in compliance with the License.

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import absolute_import, unicode_literals, print_function
from .util.version import get_version

VERSION = (0, 2, 5, '', 0)

__url__             = "http://github.com/aumayr/fava"
__version__         = get_version(VERSION)
__license__         = "MIT"
__author__          = "Dominik Aumayr"
__author_email__    = "dominik@aumayr.name"
