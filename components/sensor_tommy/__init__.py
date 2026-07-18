import shutil
import logging
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import output, esp32
from esphome.const import CONF_ID, KEY_FRAMEWORK_VERSION, KEY_CORE
from esphome.core import CORE
from pathlib import Path

SUPPORTED_ESP_IDF_VERSIONS = [
    cv.Version(5, 5, 1),
]

CONF_DISCOVERY = "discovery"
CONF_INSTANCE_IP = "instance_ip"
CONF_UDP_RELAY_PORT = "udp_relay_port"
CONF_XIAO_ESP32C6_ANTENNA = "xiao_esp32c6_antenna"

DISCOVERY_MDNS = "mdns"
DISCOVERY_MANUAL = "manual"

XIAO_ANTENNA_INTERNAL = "internal"
XIAO_ANTENNA_EXTERNAL = "external"

sensor_tommy_ns = cg.esphome_ns.namespace("sensor_tommy")
SensorTommy = sensor_tommy_ns.class_("SensorTommy", cg.Component)

_LOGGER = logging.getLogger(__name__)


def _validate_discovery(config):
    mode = config.get(CONF_DISCOVERY)
    if mode == DISCOVERY_MANUAL:
        if CONF_INSTANCE_IP not in config or not config[CONF_INSTANCE_IP].strip():
            raise cv.Invalid("instance_ip is required when discovery: manual.")
    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(SensorTommy),
            cv.Optional(CONF_DISCOVERY): cv.one_of(DISCOVERY_MDNS, DISCOVERY_MANUAL, lower=True),
            cv.Optional(CONF_INSTANCE_IP): cv.string,
            cv.Optional(CONF_UDP_RELAY_PORT): cv.port,
            cv.Optional(CONF_XIAO_ESP32C6_ANTENNA): cv.one_of(XIAO_ANTENNA_INTERNAL, XIAO_ANTENNA_EXTERNAL, lower=True),
        }
    ).extend(cv.COMPONENT_SCHEMA),
    _validate_discovery,
)


async def to_code(config):
    # Ensure ESP-IDF is being used
    if CORE.using_arduino:
        raise cv.Invalid("ESP-IDF framework is required for this component (set framework: type: esp-idf)")

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

    # Link the prebuilt archive
    cg.add_build_flag(f"-Wl,--whole-archive,{lib_dest},--no-whole-archive")

    var = cg.new_Pvariable(config[CONF_ID])

    # Get discovery mode and infer if not set explictly
    mode = config.get(CONF_DISCOVERY)
    if mode is None:
        if CONF_INSTANCE_IP in config:
            mode = DISCOVERY_MANUAL
            _LOGGER.warning(
                "sensor_tommy: 'discovery' is not set. "
                "Inferred 'manual' because 'instance_ip' is present. "
                "Set 'discovery: manual' explicitly to suppress this warning."
            )
        else:
            mode = DISCOVERY_MDNS
            _LOGGER.warning(
                "sensor_tommy: 'discovery' is not set. "
                "Defaulting to 'mdns'. "
                "Set 'discovery: mdns' explicitly to suppress this warning."
            )

    cg.add(var.set_discovery_mode(mode))

    if mode == DISCOVERY_MANUAL:
        cg.add(var.set_instance_ip(config[CONF_INSTANCE_IP]))
        if CONF_UDP_RELAY_PORT in config:
            cg.add(var.set_udp_relay_port(config[CONF_UDP_RELAY_PORT]))

    if CONF_XIAO_ESP32C6_ANTENNA in config:
        cg.add(var.set_xiao_esp32c6_antenna(config[CONF_XIAO_ESP32C6_ANTENNA]))

    await output.register_output(var, config)
    await cg.register_component(var, config)
