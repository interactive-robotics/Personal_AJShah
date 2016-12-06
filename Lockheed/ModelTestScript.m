clear all

%Define Basis information
Basis.order = 2;
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
 load ExampleTraj2.mat
%  
%  TrajEntryTable = (NewDomain.Trajectory(2,:));
%  TrajEntry.t = TrajEntryTable.t;
%  TrajEntry.X = [TrajEntryTable.x;TrajEntryTable.y;TrajEntryTable.theta];
%  TrajEntry.reward = TrajEntryTable.reward;
%  TrajEntry.U = TrajEntryTable.control;
%  
%  NewModel.ReceiveNewTrajEntry(TrajEntry);
%  
%   TrajEntryTable = (NewDomain.Trajectory(3,:));
%  TrajEntry.t = TrajEntryTable.t;
%  TrajEntry.X = [TrajEntryTable.x;TrajEntryTable.y;TrajEntryTable.theta];
%  TrajEntry.reward = TrajEntryTable.reward;
%  TrajEntry.U = TrajEntryTable.control;
%  
%  NewModel.ReceiveNewTrajEntry(TrajEntry);

for i = 2:200
    TrajEntryTable = (NewDomain.Trajectory(i,:));
    TrajEntry.t = TrajEntryTable.t;
    TrajEntry.X = [TrajEntryTable.x;TrajEntryTable.y;TrajEntryTable.theta];
    TrajEntry.reward = TrajEntryTable.reward;
    TrajEntry.U = TrajEntryTable.control;
    NewModel.ReceiveNewTrajEntry(TrajEntry);
end

sum_rq = [NewModel.Statistics(:).sum_rq];
close all

plot(sum_rq)
NewModel.ComputeModelEvidence(NewModel.tCurrent,190);
