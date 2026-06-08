#ifndef TOMMY_START_H
#define TOMMY_START_H

#ifdef __cplusplus
extern "C" {
#endif

void tommy_start();
void tommy_start_with_mdns();
void tommy_start_with_instance_details(const char *instance_ip, int udp_relay_port);
void tommy_set_xiao_esp32c6_antenna(const char *antenna);

#ifdef __cplusplus
}
#endif

#endif