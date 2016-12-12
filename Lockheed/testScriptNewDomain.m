close all
%Test script for class constructor
NewDomain = MissionDomain();

%Generate the start state randomly in a region
StartState.x = (-3 + 5)*rand(1,1) -5;
StartState.y = (-1 + 2)*rand(1,1) -2;
StartState.theta = 2*pi*rand(1,1) -pi;
NewDomain.SetStartState(StartState);

%Generate Waypoints
Waypoint = struct('x',{},'y',{});
Waypoint(1).x = 0;
Waypoint(1).y = 0;

Waypoint(2).x = 1;
Waypoint(2).y = 1;

Waypoint(3).x = 1;
Waypoint(3).y = 2;

Waypoint(4).x = -3;
Waypoint(4).y = 4;

NewDomain.SetWaypoints(Waypoint);
% for i = 1:100
% NewDomain.PropogateState(NewDomain.HeadingControl(1))
% end
%NewDomain.PlotDomain

NewDomain.Plan();
%Plot the domain trajectory
NewDomain.PlotDomain

%plot the the control input throughout the trajectory
figure
plot(NewDomain.Trajectory.t,NewDomain.Trajectory.control)

%plot the reward signal accrued
figure
plot(NewDomain.Trajectory.t, NewDomain.Trajectory.reward)

%plot the accrued reward as per a discount factor
lambda = 0.9;
nSteps = length(NewDomain.Trajectory.t);
AccruedReward = zeros(nSteps,1);
multiplier = 1;
AccruedReward(1) = NewDomain.Trajectory.reward(1);
for i=1:nSteps-1
    multiplier = multiplier*lambda;
    AccruedReward(i+1) = AccruedReward(i) + multiplier*NewDomain.Trajectory.reward(i+1);
end
figure
plot(NewDomain.Trajectory.t,AccruedReward)