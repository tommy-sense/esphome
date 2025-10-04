#pragma once

#include "esphome/core/component.h"

namespace esphome {
namespace sensor_tommy {

class SensorTommy : public Component {
 public:
  float get_setup_priority() const override; 
  void setup() override;
  void loop() override;
  void dump_config() override;
};

} 
}