# Required configuration:
The following options need to be set for TOMMY to work correctly.

```yaml
esphome:
  ...

esp32:
  ...
  framework:
    version: 5.4.2
    sdkconfig_options:
      CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM: '128'
      CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM: '128'
      CONFIG_ESP_WIFI_CSI_ENABLED: y
      CONFIG_ESP_WIFI_AMPDU_TX_ENABLED: n
      CONFIG_ESP_WIFI_AMPDU_RX_ENABLED: n
      CONFIG_ESP_WIFI_STA_DISCONNECTED_PM_ENABLE: n
      CONFIG_PM_ENABLE: n
    type: esp-idf

wifi:
  ...
  power_save_mode: NONE

external_components:
  - source: github://tommy-sense/esphome
    components: [ sensor_tommy ]
  
sensor_tommy:
```
