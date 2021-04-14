# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "TCP Server",
    "author": "Tim Kruse (based on blender_cloud addon by Sybren A. Stüvel, Francesco Siddi, Inês Almeida, Antony Riakiotakis",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Operator search",
    "description": "Background TCP Server to stream data into blender",
    "category": "System",
}

import logging
log = logging.getLogger(__name__)


def register():
    """Late-loads and registers the Blender-dependent submodules."""

    import sys


    # Support reloading
    if "%s.blender" % __name__ in sys.modules:
        import importlib

        def reload_mod(name):
            modname = "%s.%s" % (__name__, name)
            try:
                old_module = sys.modules[modname]
            except KeyError:
                # Wasn't loaded before -- can happen after an upgrade.
                new_module = importlib.import_module(modname)
            else:
                new_module = importlib.reload(old_module)

            sys.modules[modname] = new_module
            return new_module


        async_loop = reload_mod("async_loop")
        tcp_server = reload_mod("tcp_server")
    else:
        from . import (async_loop, tcp_server)

    async_loop.setup_asyncio_executor()
    async_loop.register()
    tcp_server.register()

def unregister():
    from . import (async_loop, tcp_server)
    async_loop.unregister()
    tcp_server.unregister()
