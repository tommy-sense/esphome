#include "sensor_tommy.h"

#include <cstring>

#include "esphome/components/network/util.h"
#include "esphome/core/log.h"
#include "lib.h"

namespace esphome {
namespace sensor_tommy {

static const char *TAG = "sensor_tommy.component";

void SensorTommy::setup() {}

void SensorTommy::loop() {
  if (network::is_connected()) {
    if (!instance_ip_.empty() && this->udp_relay_port_ != 0) {
      tommy_start_with_instance_details(this->instance_ip_.c_str(), this->udp_relay_port_);
    } else {
      tommy_start();
    }

    this->disable_loop();
  }
}

void SensorTommy::dump_config() {
  ESP_LOGCONFIG(TAG, "TOMMY:");
  if (!instance_ip_.empty()) {
    ESP_LOGCONFIG(TAG, "  Instance IP: %s", this->instance_ip_.c_str());
    ESP_LOGCONFIG(TAG, "  UDP Relay Port: %d", this->udp_relay_port_);
  } else {
    ESP_LOGCONFIG(TAG, "  Using auto-discovery via mDNS");
  }
}

}  // namespace sensor_tommy
}  // namespace esphome