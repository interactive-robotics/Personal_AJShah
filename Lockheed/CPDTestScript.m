clear all
datafile = 'ExampleTraj5.mat';

%Define all the models in the CPD formulation
%Model 1:
%Define Basis information
Basis.order = 1;
Bounds(1).max = 5;
Bounds(1).min = -5;
Bounds(2).max = 5;
Bounds(2).min = -5;
Bounds(3).max = pi;
Bounds(3).min = -pi;
Basis.Bounds = Bounds;
Basis.dimension = 3;

%Define Parameters

Params.delta = 0.0001;
%Params.sigma2v = 1;
%Params.betav = 0.01;
Params.u = 10;
Params.v = 0.5;
Params.SkillLength = 100;
Params.discount = 0.9;

NewModel = Model(Params,Basis);

% Create the NewCPD.Models array
Models(1,1) = NewModel;
ModelPriors = 1;
CPDParameters.skillLength = 100;
%Create the CPD Object
NewCPD = CPD(Models,ModelPriors,CPDParameters);

load(datafile)
% TrajEntryTable = (NewDomain.Trajectory(2,:));
% TrajEntry.t = TrajEntryTable.t;
% TrajEntry.X = [TrajEntryTable.x;TrajEntryTable.y;TrajEntryTable.theta];
% TrajEntry.reward = TrajEntryTable.reward;
% TrajEntry.U = TrajEntryTable.control;
% 
% NewCPD.ReceiveTrajectory(TrajEntry);

Tmax = size(NewDomain.Trajectory,1);

for i = 2:Tmax
    TrajEntryTable = (NewDomain.Trajectory(i,:));
    TrajEntry.t = TrajEntryTable.t;
    TrajEntry.X = [TrajEntryTable.x;TrajEntryTable.y;TrajEntryTable.theta];
    TrajEntry.reward = TrajEntryTable.reward;
    TrajEntry.U = TrajEntryTable.control;
    NewCPD.ReceiveTrajectory(TrajEntry);
end

Changepoints = NewCPD.LookBack();
NewDomain.PlotChangepoints(Changepoints)
