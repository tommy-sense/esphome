#pragma once

#include <string>

#include "esphome/core/component.h"

namespace esphome {
namespace sensor_tommy {

class SensorTommy : public Component {
 public:
  void setup() override;
  void loop() override;
  void dump_config() override;

  void set_instance_ip(const std::string &ip) { this->instance_ip_ = ip; }
  void set_udp_relay_port(int port) { this->udp_relay_port_ = port; }

 protected:
  std::string instance_ip_;
  int udp_relay_port_ = 0;
};

}  // namespace sensor_tommy
}  // namespace esphome