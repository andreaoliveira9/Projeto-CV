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

    set_global_font_scale(1.15)  # Slightly larger font for better readability

    # Main Theme
    with theme() as main_theme:
        with theme_component(mvAll):
            add_theme_color(mvThemeCol_WindowBg, [45, 45, 48, 255])
            add_theme_color(mvThemeCol_Border, [100, 100, 100, 255])
            add_theme_color(mvThemeCol_FrameBg, [50, 50, 50, 255])
            add_theme_color(mvThemeCol_FrameBgHovered, [70, 70, 70, 255])
            add_theme_color(mvThemeCol_FrameBgActive, [90, 90, 90, 255])
            add_theme_color(mvThemeCol_Button, [100, 150, 200, 255])
            add_theme_color(mvThemeCol_ButtonHovered, [120, 170, 220, 255])
            add_theme_color(mvThemeCol_ButtonActive, [140, 190, 240, 255])
            add_theme_style(mvStyleVar_FrameRounding, 5.0)  # Rounded corners
            add_theme_style(mvStyleVar_FramePadding, 8.0, 4.0)
            add_theme_style(mvStyleVar_ItemSpacing, 10.0, 10.0)

    # Slider Theme
    with theme() as slider_theme:
        with theme_component(mvSliderFloat):
            add_theme_color(mvThemeCol_SliderGrab, [100, 150, 200, 255])
            add_theme_color(mvThemeCol_SliderGrabActive, [60, 90, 130, 255])
            add_theme_color(mvThemeCol_FrameBg, [50, 50, 50, 255])
            add_theme_color(mvThemeCol_FrameBgHovered, [70, 70, 70, 255])

    # Create Window and capture its ID
    with window(label="Shader Parameter Control", width=450, height=300) as window_id:
        add_text("Control Panel for Shader Parameters", color=[200, 200, 200, 255])
        add_separator()

        # Section Header
        add_text("Adjust Blend Strength", color=[100, 200, 255], bullet=True)

        # Add Slider and bind its theme
        slider_id = add_slider_float(
            label="Blend Strength",
            min_value=0.0,
            max_value=3.0,
            default_value=2.0,
            callback=update_blend_strength,
            width=300,
        )
        bind_item_theme(slider_id, slider_theme)

        # Footer
        add_separator()
        add_text("Adjust the slider above to update the shader parameter in real-time.")

    # Bind theme to the window using the captured ID
    bind_item_theme(window_id, main_theme)

    create_viewport(
        title="Shader Parameter Control",
        width=450,
        height=300,
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
