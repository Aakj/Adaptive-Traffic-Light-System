# CS659A_Adaptive_Traffic_Control

CS659A Project : Adaptive Traffic Control

Our project focuses on implementing a learning algorithm (DQN) that will allow traffic control devices to study traffic patterns or behaviors for a given intersection and optimize traffic flow by timely change of phases.

We have considered three primary operational modes for traffic signals:
1. Pre-timed
2. Actuated
3. DQN (Deep Q-Network)

In order to run a specific mode for a particular flow rate:
1. Move inside the specific mode's folder.
2. Set the vehsPerHour (flow rate) in the file (extension rou.xml).
3. Run main.py 

You can see the GUI version by setting the input to "sumo-gui" in main.py file.
