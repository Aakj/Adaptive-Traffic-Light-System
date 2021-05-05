# Helper function to generate routes with different flows dynamically for training
def generateFlowRoute(flowRate_hi,flowRate_lo):
    fId=open("trainDemands.rou.xml","w")
    fId.write(r'<?xml version="1.0" encoding="UTF-8"?>'+"\n")
    fId.write(r'<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">'+"\n")
    fId.write(r'<route edges="edge_LR_1 edge_LR_2" color="yellow" id="route_0"/>'+"\n")
    fId.write(r'<route edges="edge_RL_1 edge_RL_2" color="yellow" id="route_1"/>'+"\n")
    fId.write(r'<route edges="edge_NS_1 edge_NS_2" color="yellow" id="route_2"/>'+"\n")
    fId.write(r'<route edges="edge_SN_1 edge_SN_2" color="yellow" id="route_3"/>'+"\n")
    fId.write(r'<flow id="flow_LR" begin="0.00" route="route_0" end="86400" vehsPerHour="{}"/>'.format(flowRate_lo)+"\n")
    fId.write(r'<flow id="flow_RL" begin="0.00" route="route_1" end="86400" vehsPerHour="{}"/>'.format(flowRate_lo)+"\n")
    fId.write(r'<flow id="flow_NS" begin="0.00" route="route_2" end="86400" vehsPerHour="{}"/>'.format(flowRate_hi)+"\n")
    fId.write(r'<flow id="flow_SN" begin="0.00" route="route_3" end="86400" vehsPerHour="{}"/>'.format(flowRate_hi)+"\n")
    fId.write(r'</routes>'+"\n")
    fId.close()

    return

