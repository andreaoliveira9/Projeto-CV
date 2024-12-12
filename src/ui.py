import asyncio
import websockets
from dearpygui.dearpygui import *


async def send_parameter_update(parameter, value):
    """Send parameter update message to the WebSocket server."""
    message = f"{parameter}:{value}"
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send(message)


def update_blend_strength(sender, app_data):
    """Callback to handle blend strength slider changes."""
    blend_strength = app_data
    asyncio.run(send_parameter_update("change_blend_strength", blend_strength))


def create_ui():
    """Create and display the UI."""
    create_context()

    set_global_font_scale(1.25)  # Slightly larger font

    with window(label="Shader Parameter Control", width=400, height=200, pos=[50, 50]):
        add_text("Adjust parameters to control the shader rendering.")
        add_separator()
        add_slider_float(
            label="Blend Strength",
            min_value=0.1,
            max_value=10.0,
            default_value=2.0,
            callback=update_blend_strength,
            width=300,
        )

    create_viewport(
        title="Shader Parameter Control",
        width=450,
        height=250,
        resizable=False,
    )
    setup_dearpygui()
    show_viewport()

    # Main event loop
    while is_dearpygui_running():
        render_dearpygui_frame()

    destroy_context()


if __name__ == "__main__":
    create_ui()
