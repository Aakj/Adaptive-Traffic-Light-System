import traci
from plot import DataPlotter


# StepListener class that monitors the lanes for vehicles. Captures the count of incoming and outgoing vehicles,
# and delay of incoming vehicles withing the detector distance.
# Captures the data at every "stepDuration" (3s) of simulation time.
class LaneListener(traci.StepListener):
    prevTime=0
    currTime=0
    inCounts=[]
    outCounts=[]
    inDelays=[]

    # Helper function that calculates the delay of vehicles on an edge, that is within the detector distance.
    def findDelays(self,edgeId):
        return traci.edge.getWaitingTime(edgeId)

    # Helper function that calculates the number of vehicles on an edge, that is within the detector distance.
    def countVehicles(self,edgeId):
        return traci.edge.getLastStepVehicleNumber(edgeId)
        
    def countHaltVehicles(self,edgeId):
        return traci.edge.getLastStepHaltingNumber(edgeId)


    # At every simulation step call, this function is called. 
    # Captures the Incoming Queue count, outgoing vehicle count and the delay according to the reference paper.
    def step(self,t):
        self.currTime=traci.simulation.getTime()
        if self.currTime-self.prevTime>=stepDuration:
            vhCntInStep=0
            vhCntOutStep=0
            vhDelayStep=0
            for di in dirList:
                eIn="edge_{}_1".format(di)
                eOut="edge_{}_2".format(di)
                inCount=self.countVehicles(eIn)
                inCount=inCount-self.countHaltVehicles(eIn)
                outCount=self.countVehicles(eOut)
                inDelay=self.findDelays(eIn)
                vhCntInStep+=inCount
                vhCntOutStep+=outCount
                vhDelayStep+=inDelay
            self.inCounts.append((traci.simulation.getTime(),vhCntInStep))
            self.outCounts.append((traci.simulation.getTime(),vhCntOutStep))
            self.inDelays.append((traci.simulation.getTime(),vhDelayStep))
            self.prevTime=self.currTime

        return True

    # Getter function
    def getData(self):
        retData=[None,None,None]
        retData[0]=self.inCounts
        retData[1]=self.outCounts
        retData[2]=self.inDelays
        return retData


# StepListener class that monitors the Traffic Lights and obtains the MaxOut durations
# At every step it is checked whether the traffic light switched from Green to other states.
# Green phase duration is obtained from the difference between the timestamp of going out of green phase and the timestamp when the green phase started.
# MaxOut is the green phase duration minus the minimum green phase duration.
class TrafficLightListener(traci.StepListener):
    prev_TL_state=None
    current_TL_state=None
    prev_TL_time=0.01
    current_TL_time=None
    maxOuts=[]

    # Constructor
    def __init__(self):
        super(TrafficLightListener,self).__init__()
        self.prev_TL_state=traci.trafficlight.getPhase("juncInterTL")

    # Step function that is executed after every simulationStep() call. Must always return true in order to be called at every step.
    # Captures the maxout duration of the traffic lights
    def step(self,t):
        self.current_TL_state=traci.trafficlight.getPhase("juncInterTL")
        self.current_TL_time=traci.simulation.getTime()
        if self.current_TL_state!=self.prev_TL_state:
            if self.prev_TL_state==0 or self.prev_TL_state==3:
                greenDuration=self.current_TL_time-self.prev_TL_time
                maxOut=greenDuration-minDur
                self.maxOuts.append((traci.simulation.getTime(),maxOut))
            self.prev_TL_state=self.current_TL_state
            self.prev_TL_time=self.current_TL_time
        return True

    # Getter function
    def getData(self):
        return self.maxOuts




if __name__ == '__main__':
    # Change first parameter "sumo" to "sumo-gui" to open the GUI. Change the value after "-d" to "50" or "100" to slowdown the simulation in GUI.
    sumoCmd=["sumo", "-n", "map.net.xml","-r","demands.rou.xml","--step-length","0.01","-S","-d","0.0","-Q"]
    traci.start(sumoCmd)

    # Some Simulation Parameters
    totalSimDuration=3600
    minDur=10
    stepDuration=3
    dirList=["LR","RL","NS","SN"]
    detectDist=55

    # StepListener objects which are used to execute functions at every simulation step
    tlListener=TrafficLightListener()
    laneListener=LaneListener()
    traci.addStepListener(laneListener)
    traci.addStepListener(tlListener)
    
    # Simulation loop
    while traci.simulation.getTime()<=totalSimDuration:
        traci.simulationStep()
    traci.close()


    # Plot the obtained simulation results
    maxOutData=tlListener.getData()
    laneSimData=laneListener.getData()
    dataPlot=DataPlotter(laneSimData[0],laneSimData[1],laneSimData[2],maxOutData)
    dataPlot.plotMaxOut()
    dataPlot.plotQueueLength()
    

    


    

