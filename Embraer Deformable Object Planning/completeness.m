% Completeness example script

load ExampleNode.mat
PlotStateLargeGoal2(TempNode)

nmanip = length(TempNode.State.Manipulator);

TempNode.State.Manipulator(nmanip+1).position = [1.5 1 0];
TempNode.State.Manipulator(nmanip+1).cable = [];
TempNode.State.Manipulator(nmanip+1).grip = [];

PlotStateLargeGoal2(TempNode);
