from asyncio.queues import QueueEmpty
from os import name
import bpy
import asyncio
from typing import Optional
from struct import unpack
from . import async_loop
import re

tcpserver = None
coroutine = None

class TCPProperties(bpy.types.PropertyGroup):
    addr : bpy.props.StringProperty(name="addr", description="TCP Server Address", default="127.0.0.1")
    port : bpy.props.IntProperty(name="port", description="TCP Server Port", default=55555, min=1000, max=2**16-1)


class TCPServer(asyncio.Protocol):
    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print(f"connection from {peername}")
        self.counter = 0
        
    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.transport = None
        print("connection lost")

    def data_received(self, data: bytes) -> None:
        dataQueue = bpy.types.Scene.tcpDataQueue
        dataQueue.put_nowait(data)

class VIEW3D_PT_tcpserver(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TCP Server"
    bl_label = "TCP Server"

    def draw(self, context):
        row = self.layout.row(align=True)
        props = row.operator("tcpserver.start", text="Start")
        props.server_addr = bpy.context.scene.TCPProperties.addr
        props.server_port = bpy.context.scene.TCPProperties.port
        row.operator("tcpserver.stop", text="Stop")
        self.layout.label(text="Running" if tcpserver else "Stopped")

        col = self.layout.column(align=True)
        col.prop(bpy.context.scene.TCPProperties, "addr", text="Address")
        col.prop(bpy.context.scene.TCPProperties, "port", text="Port")



class TCPSERVER_OT_tcpserver_start(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    """Start a TCP Server in the background"""
    bl_idname = "tcpserver.start"
    bl_label = "Start a TCP Server in the background"

    server_addr : bpy.props.StringProperty(name="addr", description="TCP Server Address", default="127.0.0.1")
    server_port : bpy.props.IntProperty(name="port", description="TCP Server Port", default=55555, min=1000, max=2**16-1)

    def execute(self, context):
        return self.invoke(context,None)
    
    def invoke(self, context, event):
        global tcpserver
        global coroutine
        if tcpserver is None:
            if re.search("^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$", self.server_addr):
                bpy.context.scene.TCPProperties.addr = self.server_addr
                bpy.context.scene.TCPProperties.port = self.server_port
                bpy.types.Scene.tcpDataQueue = asyncio.Queue()
                loop = asyncio.get_event_loop()
                coroutine = loop.create_server(TCPServer, self.server_addr, self.server_port)
                tcpserver = loop.run_until_complete(coroutine)
                print(f"tcp server startet {self.server_addr}:{self.server_port}")
                return async_loop.AsyncModalOperatorMixin.invoke(self, context, event)
            else:
                print("Invalid IP address")
                return {"CANCELLED"}
        else:
            print("server already started")
            return {"CANCELED"}

class TCPSERVER_OT_tcpserver_stop(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    """Stops the TCP Server"""
    bl_idname = "tcpserver.stop"
    bl_label = "Stops the TCP Server"

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        global tcpserver
        global coroutine
        if tcpserver is not None:
            tcpserver.close()
            tcpserver = None
            coroutine = None
            print("TCP Server stopped")
        else:
            print("Failed to stop TCP Server")
        
        return {"FINISHED"}

classes = (
    TCPProperties,
    TCPSERVER_OT_tcpserver_start, 
    TCPSERVER_OT_tcpserver_stop,
    VIEW3D_PT_tcpserver
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.TCPProperties = bpy.props.PointerProperty(type=TCPProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    del(bpy.types.Scene.TCPProperties)