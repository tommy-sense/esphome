import shutil
import esphome.codegen as cg
import esphome.config_validation as cv
import esphome.final_validate as fv
from esphome.components import output, esp32
from esphome.const import (
    CONF_ESPHOME,
    CONF_FRAMEWORK,
    CONF_ID,
    CONF_MIN_VERSION,
    CONF_POWER_SAVE_MODE,
    CONF_SOURCE,
    CONF_TOOLCHAIN,
    CONF_TYPE,
    CONF_VERSION,
    CONF_WIFI,
    KEY_CORE,
    KEY_FRAMEWORK_VERSION,
    PLATFORM_ESP32,
)
from esphome.core import CORE
from pathlib import Path

DOCS_URL = "https://www.tommysense.com/docs/flashing-devices/esphome"

DEPENDENCIES = ["wifi", "esp32"]
REQUIRED_MIN_VERSION = cv.Version(2026, 7, 0)
REQUIRED_TOOLCHAIN = "esp-idf"
REQUIRED_FRAMEWORK_TYPE = "esp-idf"
REQUIRED_FRAMEWORK_VERSION = "5.5.1"
REQUIRED_FRAMEWORK_SOURCE = "https://github.com/espressif/esp-idf/releases/download/v5.5.1/esp-idf-v5.5.1.zip"
REQUIRED_SDKCONFIG_OPTIONS = {
    "CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM": "128",
    "CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM": "128",
    "CONFIG_ESP_WIFI_CSI_ENABLED": "y",
    "CONFIG_ESP_WIFI_AMPDU_TX_ENABLED": "n",
    "CONFIG_ESP_WIFI_AMPDU_RX_ENABLED": "n",
    "CONFIG_ESP_WIFI_STA_DISCONNECTED_PM_ENABLE": "n",
    "CONFIG_PM_ENABLE": "n",
    "CONFIG_ESP_TASK_WDT_TIMEOUT_S": "30",
}
CONF_SDKCONFIG_OPTIONS = "sdkconfig_options"
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


def _invalid(message: str) -> cv.Invalid:
    return cv.Invalid(f"{message} See {DOCS_URL}")


def _validate_discovery(config):
    mode = config[CONF_DISCOVERY]
    if mode == DISCOVERY_MANUAL:
        if CONF_INSTANCE_IP not in config or not config[CONF_INSTANCE_IP].strip():
            raise _invalid("TOMMY: instance_ip is required when discovery: manual.")
    return config


def _final_validate(config):
    full_config = fv.full_config.get()

    esphome_conf = full_config.get(CONF_ESPHOME, {})
    min_version_raw = esphome_conf.get(CONF_MIN_VERSION)
    if min_version_raw is None:
        raise _invalid(
            f"TOMMY: esphome.{CONF_MIN_VERSION} is a requirement. " f"Set '{CONF_MIN_VERSION}: {REQUIRED_MIN_VERSION}'."
        )
    min_version = cv.Version.parse(str(min_version_raw))
    if min_version < REQUIRED_MIN_VERSION:
        raise _invalid(
            f"TOMMY: esphome.{CONF_MIN_VERSION} must be at least {REQUIRED_MIN_VERSION}. " f"Got: {min_version}."
        )

    esp32_conf = full_config.get(PLATFORM_ESP32)
    if esp32_conf is None:
        raise _invalid("TOMMY: esp32 configuration is required.")

    toolchain = esp32_conf.get(CONF_TOOLCHAIN, REQUIRED_TOOLCHAIN)
    if str(toolchain).lower() != REQUIRED_TOOLCHAIN:
        raise _invalid(f"TOMMY: esp32.{CONF_TOOLCHAIN} must be '{REQUIRED_TOOLCHAIN}'. Got: {toolchain}.")

    framework = esp32_conf.get(CONF_FRAMEWORK)
    if framework is None:
        raise _invalid(
            "TOMMY: esp32.framework is required. "
            f"Expected: (type: {REQUIRED_FRAMEWORK_TYPE}, version: {REQUIRED_FRAMEWORK_VERSION})."
        )

    framework_type = framework.get(CONF_TYPE)
    if framework_type != REQUIRED_FRAMEWORK_TYPE:
        raise _invalid(f"TOMMY: esp32.framework.type must be '{REQUIRED_FRAMEWORK_TYPE}'. " f"Got: {framework_type}.")

    framework_version = framework.get(CONF_VERSION)
    if str(framework_version) != REQUIRED_FRAMEWORK_VERSION:
        raise _invalid(
            f"TOMMY: esp32.framework.version must be '{REQUIRED_FRAMEWORK_VERSION}'. " f"Got: {framework_version}."
        )

    framework_source = framework.get(CONF_SOURCE)
    if framework_source != REQUIRED_FRAMEWORK_SOURCE:
        raise _invalid(f"TOMMY: esp32.framework.source must be set to '{REQUIRED_FRAMEWORK_SOURCE}'.")

    sdkconfig_options = framework.get(CONF_SDKCONFIG_OPTIONS, {})
    missing_or_invalid = []
    for key, expected in REQUIRED_SDKCONFIG_OPTIONS.items():
        actual = sdkconfig_options.get(key)
        if actual is None or str(actual).lower() != expected.lower():
            missing_or_invalid.append(f"{key}: '{expected}'")
    if missing_or_invalid:
        raise _invalid(
            "TOMMY: esp32.framework.sdkconfig_options is missing required values: "
            + ", ".join(missing_or_invalid)
            + "."
        )

    wifi_conf = full_config.get(CONF_WIFI)
    if wifi_conf is None:
        raise _invalid("TOMMY: wifi configuration is required.")
    power_save_mode = wifi_conf.get(CONF_POWER_SAVE_MODE)
    if power_save_mode is None or str(power_save_mode).lower() != "none":
        raise _invalid(f"TOMMY: wifi.{CONF_POWER_SAVE_MODE} must be set to 'NONE'.")

    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(SensorTommy),
            cv.Required(
                CONF_DISCOVERY,
                msg=(
                    f"TOMMY: '{CONF_DISCOVERY}' is required. "
                    f"Set '{CONF_DISCOVERY}: {DISCOVERY_MDNS}' or "
                    f"'{CONF_DISCOVERY}: {DISCOVERY_MANUAL}'. See {DOCS_URL}"
                ),
            ): cv.one_of(DISCOVERY_MDNS, DISCOVERY_MANUAL, lower=True),
            cv.Optional(CONF_INSTANCE_IP): cv.string,
            cv.Optional(CONF_UDP_RELAY_PORT): cv.port,
            cv.Optional(CONF_XIAO_ESP32C6_ANTENNA): cv.one_of(XIAO_ANTENNA_INTERNAL, XIAO_ANTENNA_EXTERNAL, lower=True),
        }
    ).extend(cv.COMPONENT_SCHEMA),
    _validate_discovery,
)

FINAL_VALIDATE_SCHEMA = _final_validate


async def to_code(config):
    # Add idf components
    esp32.add_idf_component(name="espressif/zlib", ref="^1.3.0")
    esp32.add_idf_component(name="espressif/json_parser", ref="^1.0.3")

    # Get the ESP32 variant and ESP-IDF version
    variant = CORE.config["esp32"]["variant"].lower()
    framework_version = CORE.data[KEY_CORE][KEY_FRAMEWORK_VERSION]
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
        raise _invalid(f"TOMMY: Unsupported ESP32 variant: {variant}.")

    # Copy library to build directory
    component_dir = Path(__file__).parent
    build_dir = Path(CORE.relative_build_path("src/esphome/components/sensor_tommy"))
    build_dir.mkdir(parents=True, exist_ok=True)

    lib_source = component_dir / lib_filename
    lib_dest = build_dir / lib_filename

    if not lib_source.exists():
        raise _invalid(
            f"TOMMY: Library file not found: {lib_filename} in {component_dir}. "
            f"Expected library for variant '{variant}' with ESP-IDF version {version_str}."
        )

    shutil.copy(lib_source, lib_dest)

    # Link the prebuilt archive
    cg.add_build_flag(f"-Wl,--whole-archive,{lib_dest},--no-whole-archive")

    var = cg.new_Pvariable(config[CONF_ID])

    # Get discovery mode
    mode = config[CONF_DISCOVERY]
    cg.add(var.set_discovery_mode(mode))

    # Set instance IP and UDP relay port if discovery mode is manual
    if mode == DISCOVERY_MANUAL:
        cg.add(var.set_instance_ip(config[CONF_INSTANCE_IP]))
        if CONF_UDP_RELAY_PORT in config:
            cg.add(var.set_udp_relay_port(config[CONF_UDP_RELAY_PORT]))

    if CONF_XIAO_ESP32C6_ANTENNA in config:
        cg.add(var.set_xiao_esp32c6_antenna(config[CONF_XIAO_ESP32C6_ANTENNA]))

    await output.register_output(var, config)
    await cg.register_component(var, config)
