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
  void set_file_server_http_port(int port) { this->file_server_http_port_ = port; }
  void set_file_server_https_port(int port) { this->file_server_https_port_ = port; }

 protected:
  std::string instance_ip_;
  int file_server_http_port_ = 0;
  int file_server_https_port_ = 0;
};

}  // namespace sensor_tommy
}  // namespace esphome