#include "sensor_tommy.h"

#include <cstring>

#include "esphome/components/network/util.h"
#include "esphome/core/log.h"
#include "lib.h"

namespace esphome {
namespace sensor_tommy {

static const char *TAG = "sensor_tommy.component";

void SensorTommy::setup() {
  if (!this->xiao_esp32c6_antenna_.empty()) {
    tommy_set_xiao_esp32c6_antenna(this->xiao_esp32c6_antenna_.c_str());
  }
}

void SensorTommy::loop() {
  if (network::is_connected()) {
    if (this->discovery_mode_ == "manual") {
      tommy_start_with_instance_details(this->instance_ip_.c_str(), this->udp_relay_port_);
    } else {
      tommy_start_with_mdns();
    }
    this->disable_loop();
  }
}

void SensorTommy::dump_config() {
  ESP_LOGCONFIG(TAG, "TOMMY:");
  if (this->discovery_mode_ == "manual") {
    ESP_LOGCONFIG(TAG, "  Discovery: Manual");
    ESP_LOGCONFIG(TAG, "  Instance IP: %s", this->instance_ip_.c_str());
    ESP_LOGCONFIG(TAG, "  UDP Relay Port: %d", this->udp_relay_port_);
  } else {
    ESP_LOGCONFIG(TAG, "  Discovery: mDNS");
  }
}

}  // namespace sensor_tommy
}  // namespace esphome
