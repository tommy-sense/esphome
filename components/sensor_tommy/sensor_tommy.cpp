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
    if (!instance_ip_.empty() && this->file_server_http_port_ != 0 && this->file_server_https_port_ != 0) {
        tommy_start_with_instance_details(this->instance_ip_.c_str(), this->file_server_http_port_, this->file_server_https_port_);
    } else {
        tommy_start();
    }
}

void SensorTommy::loop() {
}

void SensorTommy::dump_config() {
    ESP_LOGCONFIG(TAG, "TOMMY Sensor:");
    if (!instance_ip_.empty()) {
        ESP_LOGCONFIG(TAG, "  Instance IP: %s", this->instance_ip_.c_str());
        ESP_LOGCONFIG(TAG, "  HTTP Port: %d", this->file_server_http_port_);
        ESP_LOGCONFIG(TAG, "  HTTPS Port: %d", this->file_server_https_port_);
    } else {
        ESP_LOGCONFIG(TAG, "  Using auto-discovery via mDNS");
    }
}

} 
}