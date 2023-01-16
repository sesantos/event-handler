#!/usr/libexec/platform-python
#
# Example implementation of oper-groups.
#
# Paths:
#   interface oper-state - e.g. interface ethernet-1/{1,5} oper-state
# Options:
#   snmp-community: community to be sent in the trap. Default is public
#   snmp-trap-target: ip address of the trap receiver
#
# Example config:
#    system {
#        event-handler {
#            instance oper-group {
#                admin-state enable
#                upython-script snmp-trap-monitor.py
#                paths [
#                    "interface ethernet-1/{1..10} oper-state"
#                ]
#               options {
#                   object snmp-community {
#                       value public
#                   }
#                   object snmp-trap-target {
#                       value 10.144.214.247
#                   }
#               }
#            }
#        }
#    }
    
import sys
import json
import time


def event_handler_main(in_json_str):

    in_json = json.loads(in_json_str)
    paths = in_json['paths']
    options = in_json['options']
    persist = in_json.get('persistent-data', {})

    snmp_community=options.get('snmp-community','public')
    snmp_trap_target=options.get('snmp-trap-target','10.10.10.10')
    network_instance=options.get('network-instance','mgmt')

    response_actions = []

    local_time=time.localtime()
    time_stamp="%04d-%02d-%02d %02d:%02d:%02d"%(local_time[0:6])

    for path_value in paths:
        path_history = persist.get(path_value['path'], [])
        # record if we have no history or the value has changed
        if len(path_history) == 0 or path_history[0]['value'] != path_value['value']:
            path_history.insert(0,{'date': time_stamp, 'value' : path_value['value']})
            # trim history
            persist.update({path_value['path']: path_history})
            
            path=path_value['path']
            interface_name=path.split(" ")[1]
            if path_value['value'] == 'up':
                response_actions.append({'run-script' : {'cmdline':'/opt/srlinux/eventmgr/send_trap.sh {0} {1} {2} {3} {4} {5} &'.format(snmp_community,snmp_trap_target,'linkUp',interface_name,1,network_instance)}})

            if path_value['value'] == 'down':
                response_actions.append({'run-script' : {'cmdline':'/opt/srlinux/eventmgr/send_trap.sh {0} {1} {2} {3} {4} {5} &'.format(snmp_community,snmp_trap_target,'linkDown',interface_name,2,network_instance)}})


    response = {'actions':response_actions,'persistent-data':persist}
    return json.dumps(response)

#
# This code is only if you want to test it from bash - this isn't used when invoked from SRL
#
def main():
    example_in_json_str = """
{
    "paths": [
        {
            "path": "interface ethernet-1/1 oper-status",
            "value": "up"
        },
        {
            "path": "interface ethernet-1/2 oper-status",
            "value": "up"
        }
    ],
    "options": {
        "snmp-community": "public",
        "snmp-trap-target": "10.144.200.252"
    },
    "persistent-data": {
        "interface ethernet-1/2 oper-state": [
            {
                "value": "up",
                "date": "2022-10-11 17:22:12"
            }
        ],
        "interface ethernet-1/1 oper-state": [
            {
                "value": "down",
                "date": "2022-10-11 17:22:12"
            }
        ]
    }
}"""
    json_response = event_handler_main(example_in_json_str)
    print(f"Response JSON:\n{json_response}")


if __name__ == "__main__":
    sys.exit(main())
