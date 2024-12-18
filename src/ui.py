import asyncio
import websockets
from dearpygui.dearpygui import *


async def send_parameter(parameter, value):
    """Send parameter update message to the WebSocket server."""
    message = f"{parameter}:{value}"
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send(message)


def update_blend_strength(sender, app_data):
    """Callback to handle blend strength slider changes."""
    blend_strength = app_data
    asyncio.run(send_parameter("change_blend_strength", blend_strength))


def update_brightness(sender, app_data):
    brightness = app_data
    asyncio.run(send_parameter("change_brightness", brightness))


def update_shadowIntensity(sender, app_data):
    shadowIntensity = app_data
    asyncio.run(send_parameter("change_shadowIntensity", shadowIntensity))


def update_global_light_dir(sender, app_data):
    global_light_dir = (get_value("X"), get_value("Y"), get_value("Z"))
    asyncio.run(send_parameter("update_global_light_dir", global_light_dir))


def update_move_cube(sender, app_data):
    move_cube = (get_value("move_X"), get_value("move_Y"), get_value("move_Z"))

    type_map = {"Sin": 0, "Cos": 1}
    func_type = (
        type_map[get_value("Function_X")],
        type_map[get_value("Function_Y")],
        type_map[get_value("Function_Z")],
    )

    move_data = f"{func_type[0]}{move_cube[0]},{func_type[1]}{move_cube[1]},{func_type[2]}{move_cube[2]}"
    asyncio.run(send_parameter("update_move_cube", move_data))


def update_reflection(sender, app_data):
    reflection = (get_value("Reflection_Steps"), get_value("Reflection_Intensity"))
    asyncio.run(send_parameter("update_reflection", reflection))


def add_primitive(sender, app_data):
    """Callback to handle primitive addition."""
    primitive_type = get_value("Primitive Type")
    position = (get_value("Pos X"), get_value("Pos Y"), get_value("Pos Z"))
    radius = get_value("Radius")

    # Map primitive type to integer (0 = Sphere, 1 = Rounded Cube)
    type_map = {"Sphere": 0, "Rounded Cube": 1}
    primitive_type_id = type_map[primitive_type]

    # Format data for WebSocket
    primitive_data = (
        f"{primitive_type_id},{position[0]},{position[1]},{position[2]},{radius}"
    )
    asyncio.run(send_parameter("add_primitive", primitive_data))


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
    with window(label="Shader Parameter Control", width=450, height=550) as window_id:
        add_text("Control Panel for Shader Parameters", color=[200, 200, 200, 255])
        add_separator()

        # Blend Strength Section
        add_text("Adjust Blend Strength", color=[100, 200, 255], bullet=True)
        slider_id = add_slider_float(
            label="Blend Strength",
            min_value=0.0,
            max_value=3.0,
            default_value=2.0,
            callback=update_blend_strength,
            width=300,
        )
        bind_item_theme(slider_id, slider_theme)

        add_text("Adjust Brightness", color=[100, 200, 255], bullet=True)
        slider_id = add_slider_float(
            label="Brightness",
            min_value=0.0,
            max_value=10.0,
            default_value=1.0,
            callback=update_brightness,
            width=300,
        )
        bind_item_theme(slider_id, slider_theme)

        add_text("Adjust Shadow Intensity", color=[100, 200, 255], bullet=True)
        slider_id = add_slider_float(
            label="Shadow Intendity",
            min_value=0.0,
            max_value=1.0,
            default_value=0.2,
            callback=update_shadowIntensity,
            width=300,
        )
        bind_item_theme(slider_id, slider_theme)

        add_text(
            "Adjust Global Illumination Direction", color=[100, 200, 255], bullet=True
        )
        slider_id = add_slider_float(
            label="X",
            min_value=-1.0,
            max_value=1.0,
            default_value=0.0,
            callback=update_global_light_dir,
            width=300,
            tag="X",
        )
        bind_item_theme(slider_id, slider_theme)
        slider_id = add_slider_float(
            label="Y",
            min_value=-1.0,
            max_value=1.0,
            default_value=1.0,
            callback=update_global_light_dir,
            width=300,
            tag="Y",
        )
        bind_item_theme(slider_id, slider_theme)
        slider_id = add_slider_float(
            label="Z",
            min_value=-1.0,
            max_value=1.0,
            default_value=0.0,
            callback=update_global_light_dir,
            width=300,
            tag="Z",
        )
        bind_item_theme(slider_id, slider_theme)

        add_text("Adjust Reflection", color=[100, 200, 255], bullet=True)
        add_input_int(
            label="Relection Steps",
            width=100,
            default_value=2,
            callback=update_reflection,
            tag="Reflection_Steps",
        )
        slider_id = add_slider_float(
            label="Reflection Intensity",
            min_value=-0.0,
            max_value=1.0,
            default_value=0.5,
            callback=update_reflection,
            width=300,
            tag="Reflection_Intensity",
        )

        add_text("Adjust Cube Movement", color=[100, 200, 255], bullet=True)
        slider_id = add_slider_float(
            label="X",
            min_value=-0.0,
            max_value=5.0,
            default_value=0.0,
            callback=update_move_cube,
            width=300,
            tag="move_X",
        )
        bind_item_theme(slider_id, slider_theme)
        slider_id = add_slider_float(
            label="Y",
            min_value=-0.0,
            max_value=5.0,
            default_value=0.0,
            callback=update_move_cube,
            width=300,
            tag="move_Y",
        )
        bind_item_theme(slider_id, slider_theme)
        slider_id = add_slider_float(
            label="Z",
            min_value=-0.0,
            max_value=5.0,
            default_value=0.0,
            callback=update_move_cube,
            width=300,
            tag="move_Z",
        )
        bind_item_theme(slider_id, slider_theme)
        add_combo(
            label="Function X",
            items=["Sin", "Cos"],
            default_value="Sin",
            callback=update_move_cube,
            width=200,
            tag="Function_X",
        )
        add_combo(
            label="Function Y",
            items=["Sin", "Cos"],
            default_value="Sin",
            callback=update_move_cube,
            width=200,
            tag="Function_Y",
        )
        add_combo(
            label="Function Z",
            items=["Sin", "Cos"],
            default_value="Sin",
            callback=update_move_cube,
            width=200,
            tag="Function_Z",
        )

        # Add Primitive Section
        add_separator()
        add_text("Add a Primitive", color=[100, 200, 255], bullet=True)

        add_combo(
            label="Primitive Type",
            items=["Sphere", "Rounded Cube"],
            default_value="Sphere",
            width=200,
            tag="Primitive Type",
        )

        add_text("Position", color=[100, 200, 255], bullet=True)
        add_input_float(label="Pos X", width=100, tag="Pos X")
        add_input_float(label="Pos Y", width=100, tag="Pos Y")
        add_input_float(label="Pos Z", width=100, tag="Pos Z")

        add_input_float(label="Radius", default_value=0.0, width=100, tag="Radius")

        add_button(label="Add Primitive", callback=add_primitive)

    # Bind theme to the window using the captured ID
    bind_item_theme(window_id, main_theme)

    create_viewport(
        title="Shader Parameter Control",
        width=450,
        height=550,
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
