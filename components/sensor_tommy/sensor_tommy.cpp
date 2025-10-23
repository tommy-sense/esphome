#include "esphome/core/log.h"
#include "sensor_tommy.h"
#include "lib.h"
#include <cstring>

namespace esphome {
namespace sensor_tommy {

static const char *TAG = "sensor_tommy.component";

float SensorTommy::get_setup_priority() const {
    return setup_priority::LATE;
}

void SensorTommy::setup(){
    tommy_start();
}

void SensorTommy::loop() {
}

void SensorTommy::dump_config() {
}

} 
}