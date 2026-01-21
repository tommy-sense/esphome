import shutil
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import output, esp32
from esphome.const import CONF_ID, KEY_FRAMEWORK_VERSION, KEY_CORE
from esphome.core import CORE
from pathlib import Path

SUPPORTED_ESP_IDF_VERSIONS = [
    cv.Version(5, 5, 2),
]

CONF_INSTANCE_IP = "instance_ip"
CONF_FILE_SERVER_HTTP_PORT = "file_server_http_port"
CONF_FILE_SERVER_HTTPS_PORT = "file_server_https_port"

sensor_tommy_ns = cg.esphome_ns.namespace("sensor_tommy")
SensorTommy = sensor_tommy_ns.class_("SensorTommy", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(SensorTommy),
        cv.Optional(CONF_INSTANCE_IP): cv.string,
        cv.Optional(CONF_FILE_SERVER_HTTP_PORT): cv.port,
        cv.Optional(CONF_FILE_SERVER_HTTPS_PORT): cv.port,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    # Ensure ESP-IDF is being used
    if not CORE.using_esp_idf:
        raise cv.Invalid("ESP-IDF is required for this component")

    # Get framework version and ensure it's supported
    framework_version = CORE.data[KEY_CORE][KEY_FRAMEWORK_VERSION]
    if framework_version not in SUPPORTED_ESP_IDF_VERSIONS:
        supported_versions_str = ", ".join(str(v) for v in SUPPORTED_ESP_IDF_VERSIONS)
        raise cv.Invalid(
            f"Framework version is not supported. Expected one of: {supported_versions_str}, got: {framework_version}"
        )

    # Add idf components
    esp32.add_idf_component(name="espressif/zlib", ref="^1.3.0")
    esp32.add_idf_component(name="espressif/json_parser", ref="^1.0.3")

    # Get the ESP32 variant and ESP-IDF version
    variant = CORE.config["esp32"]["variant"].lower()

    # Format version string for library filename
    version_str = f"v{framework_version.major}.{framework_version.minor}.{framework_version.patch}"

    lib_mapping = {
        "esp32": f"esp32-{version_str}.a",
        "esp32c3": f"esp32c3-{version_str}.a",
        "esp32c5": f"esp32c5-{version_str}.a",
        "esp32c6": f"esp32c6-{version_str}.a",
        "esp32s2": f"esp32s2-{version_str}.a",
        "esp32s3": f"esp32s3-{version_str}.a",
    }

    lib_filename = lib_mapping.get(variant)
    if not lib_filename:
        raise cv.Invalid(f"Unsupported ESP32 variant for sensor_tommy: {variant}")

    # Copy library to build directory
    component_dir = Path(__file__).parent
    build_dir = Path(CORE.relative_build_path("src/esphome/components/sensor_tommy"))
    build_dir.mkdir(parents=True, exist_ok=True)

    lib_source = component_dir / lib_filename
    lib_dest = build_dir / lib_filename

    if not lib_source.exists():
        raise cv.Invalid(
            f"Library file not found: {lib_filename} in {component_dir}. "
            f"Expected library for variant '{variant}' with ESP-IDF version {version_str}"
        )

    shutil.copy(lib_source, lib_dest)

    # Add library as extra linking archive - only for main app
    cg.add_platformio_option("extra_scripts", ["post:add_tommy_lib.py"])

    # Create the extra script
    script_path = Path(CORE.relative_build_path("add_tommy_lib.py"))
    script_content = f"""
Import("env")

# Check if this is the firmware build (not bootloader)
if env.get("PROGNAME") == "firmware":
    env.Append(LINKFLAGS=[
        "-Wl,--whole-archive",
        "{lib_dest}",
        "-Wl,--no-whole-archive"
    ])
"""
    script_path.write_text(script_content)

    var = cg.new_Pvariable(config[CONF_ID])

    # Set instance configuration if provided
    if CONF_INSTANCE_IP in config:
        cg.add(var.set_instance_ip(config[CONF_INSTANCE_IP]))
    if CONF_FILE_SERVER_HTTP_PORT in config:
        cg.add(var.set_file_server_http_port(config[CONF_FILE_SERVER_HTTP_PORT]))
    if CONF_FILE_SERVER_HTTPS_PORT in config:
        cg.add(var.set_file_server_https_port(config[CONF_FILE_SERVER_HTTPS_PORT]))

    await output.register_output(var, config)
    await cg.register_component(var, config)
