import traci
from plot import DataPlotter
from DQN import DQN
import numpy as np
from tensorflow import keras
from flowRoute import generateFlowRoute

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
                inCount=inCount-self.countHaltVehicles(eIn)-1
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

        
# count incoming vehicles
def countVQ(edgeId):
        return traci.edge.getLastStepVehicleNumber(edgeId)


# reward function
def calcReward(inCnt,outCnt,inDelay):
    w1=1
    w2=-0.5
    w3=0
    reward=(w1*inCnt)+(w2*inDelay)+(w3*outCnt)
    return reward

# function to train the DQN model.
def train_model():
    episodes=10
    dqn=DQN()
    dynamicFlowArr_hi=np.random.choice(range(1200,2000),size=episodes)
    dynamicFlowArr_lo=np.random.choice(range(200,700),size=episodes)
    modelStep=3
    for trial,flow_hi,flow_lo in zip(range(episodes),dynamicFlowArr_hi,dynamicFlowArr_lo):
        generateFlowRoute(flow_hi,flow_lo)
        print("Training episode : {} having flow rates {} {}".format(trial,flow_hi,flow_lo))
        sumoCmd=["sumo", "-n", "map.net.xml","-r","trainDemands.rou.xml","--step-length","0.01","-S","-d","0.0","-Q","--no-step-log"]      
        traci.start(sumoCmd)
        lanelisten=LaneListener()
        traci.addStepListener(lanelisten)
        traci.trafficlight.setPhase("juncInterTL",0)
        totalVC=0
        for di in dirList:
            eIn="edge_{}_1".format(di)
            inCount=countVQ(eIn)
            totalVC+=inCount

        cur_state=np.array([totalVC]).reshape(1,1)
        action=0
        prevT=0.01
        done=False
        while traci.simulation.getTime()<=totalSimDuration:
            traci.simulationStep()
            if(traci.simulation.getTime()-prevT>=modelStep):
                reward=calcReward(lanelisten.getData()[0][-1][1],lanelisten.getData()[1][-1][1],lanelisten.getData()[2][-1][1])
                totalVC=0
                for di in dirList:
                    eIn="edge_{}_1".format(di)
                    inCount=countVQ(eIn)
                    totalVC+=inCount
                new_state=np.array([totalVC]).reshape(1,1)
                dqn.remember(cur_state,action,reward,new_state,done)
                dqn.replay()
                dqn.target_train()

                action=dqn.act(cur_state)
                print("train action : {} ".format(action))
                if action==0:
                    modelStep=3
                else:
                    modelStep=15
                    curTLphase=traci.trafficlight.getPhase("juncInterTL")
                    if curTLphase!=0 and curTLphase!=3:
                        action=0
                        modelStep=3
                    else:
                        traci.trafficlight.setPhase("juncInterTL",(curTLphase+1))
                cur_state=np.array([new_state]).reshape(1,1)
                prevT=traci.simulation.getTime()

        done=True
        reward=calcReward(lanelisten.getData()[0][-1][1],lanelisten.getData()[1][-1][1],lanelisten.getData()[2][-1][1])
        totalVC=0
        for di in dirList:
            eIn="edge_{}_1".format(di)
            inCount=countVQ(eIn)
            totalVC+=inCount
        new_state=np.array([totalVC]).reshape(1,1)
        dqn.remember(cur_state,action,reward,new_state,done)
        dqn.replay()
        dqn.target_train()

        traci.close()

    print("Training complete! Saving Model!")
    dqn.save_model("model")

                



if __name__ == '__main__':
    # Some Simulation Parameters
    totalSimDuration=3600
    minDur=10
    stepDuration=3
    dirList=["LR","RL","NS","SN"]
    detectDist=55

    # wantToTrain=input("Enter (1) to train, or  (2) to test : ")
    wantToTrain=2
    if wantToTrain=="1":
        train_model()
    else:
        model = keras.models.load_model('model')
        print("Loading model...")
        model.summary()
        

        # Change first parameter "sumo" to "sumo-gui" to open the GUI. Change the value after "-d" to "50" or "100" to slowdown the simulation in GUI.
        sumoCmd=["sumo-gui", "-n", "map.net.xml","-r","testDemands.rou.xml","--step-length","0.01","-S","-d","50.0","-Q"]      
        traci.start(sumoCmd)


        # StepListener objects which are used to execute functions at every simulation step
        tlListener=TrafficLightListener()
        laneListener=LaneListener()
        traci.addStepListener(laneListener)
        traci.addStepListener(tlListener)
        
        # Simulation loop
        predStep=3
        prevT=0.1
        traci.trafficlight.setPhase("juncInterTL",0)
        while traci.simulation.getTime()<=totalSimDuration:
            traci.simulationStep()
            if traci.simulation.getTime()-prevT>=predStep:
                totalVC=0
                for di in dirList:
                    eIn="edge_{}_1".format(di)
                    inCount=countVQ(eIn)
                    totalVC+=inCount
                inputState=np.array([totalVC]).reshape(1,1)
                action=np.argmax(model.predict(inputState))
                if action==0:
                    print("action 0 at {}".format(traci.simulation.getTime()))
                    predStep=3
                else:
                    predStep=15
                    curTLphase=traci.trafficlight.getPhase("juncInterTL")
                    if curTLphase!=0 and curTLphase!=3:
                        print("action 0 at {}".format(traci.simulation.getTime()))
                        action=0
                        predStep=3
                    else:
                        print("action 1 at {}".format(traci.simulation.getTime()))
                        traci.trafficlight.setPhase("juncInterTL",(curTLphase+1))
                prevT=traci.simulation.getTime()
        traci.close()


        # Plot the obtained simulation results
        maxOutData=tlListener.getData()
        laneSimData=laneListener.getData()
        dataPlot=DataPlotter(laneSimData[0],laneSimData[1],laneSimData[2],maxOutData)
        dataPlot.plotMaxOut()
        dataPlot.plotQueueLength()
        

    


    

