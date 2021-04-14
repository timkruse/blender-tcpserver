# TCP Server Addon for Blender

This addon provides a gateway to send/stream data via TCP into blender in the background without the UI to freeze.
The data can then be used inside the blender scripts.

>**Disclaimer**: The underlying code (async_loop) is taken from the [blender cloud addon](https://cloud.blender.org/services).

## Installation

1. Download this addon.
2. In blender go to `Edit` -> `Preferences` -> `Add-ons` -> `Install...` -> Select the folder/zip of this addon -> Press `Install addon`
3. Search for this addon and enable it.

## Usage

In the 3D Viewport press `N` to toggle the context and open the `TCP Server Panel`.
Adjust or leave the address and port and press `Start`.
Now the server accepts data from a client (see examples/test_client.py).
Incoming data is put into a Queue / FIFO.
The data is accessed from within scripts via 

```python
dataQueue = bpy.types.Scene.tcpDataQueue
if not dataQueue.empty():
    bytes = dataQueue.get_nowait()
```

The type of `dataQueue` is asyncio.Queue.


## Bugs

During testing the Server did not shut down / stop correctly under some circumstances.
Which means that the tcp socket is not freed and blender had to be restarted to restart the TCP Server again.