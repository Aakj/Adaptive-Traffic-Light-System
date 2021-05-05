import matplotlib.pyplot as plt

# Helper class for plotting the obtained data.
class DataPlotter():
    maxOutArr=None
    inCounts=None
    outCounts=None
    inDelays=None

    def __init__(self,vhCntIn,vhCntOut,vhDelays,maxOutDuration):
        self.maxOutArr=maxOutDuration
        self.inCounts=vhCntIn
        self.outCounts=vhCntOut
        self.inDelays=vhDelays

    # Plots the max out values obtained in the simulation across time
    def plotMaxOut(self):
        fig=plt.figure(figsize=(20,20))
        tstamps=[x[0] for x in self.maxOutArr]
        maxouts=[x[1] for x in self.maxOutArr]
        plt.plot(tstamps,maxouts)
        fig.savefig("drlPlotMaxout.jpg")
    
    # Plots the incoming vehicle queue counts across time
    def plotQueueLength(self):
        fig=plt.figure(figsize=(20,20))
        tstamps=[x[0] for x in self.inCounts]
        queueL=[x[1] for x in self.inCounts]
        plt.plot(tstamps,queueL)
        plt.xlabel("Simulation Time (s)",fontsize=35)
        plt.ylabel("Total Queue Length",fontsize=35)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        fig.savefig("drlPlotQueueLength.jpg")

