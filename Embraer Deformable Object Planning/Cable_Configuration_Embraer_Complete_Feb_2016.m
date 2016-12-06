clear all;

% This script creates the cable model for the Embraer fuselage between
% fuselage frames 51 and 81 (after the emergency exit).

%We first define the frame positions and the cable heights. Cable heights
%and the reference points will be identically located for all the cables

FramePos = [17.100 17.550 17.990 18.415 18.850 19.298 19.602 20.052 20.432 20.857 21.209...
    21.634 21.883 22.308 22.660 23.085 23.334 23.759 24.139 24.564 24.944 25.369...
    25.749 26.174 26.554 26.979 27.359 27.784 28.164 28.589];

FrameNos = [51:58 60:81];

CableHeight = [0.2012 0.2661 0.4218 0.5119];

FramePosOrig = FramePos - FramePos(1);
diffFramePos = diff(FramePosOrig);

nFrames = length(FramePos);

multiplier = 1.052; %This factor defines the relative slack in the cable

% Cable 1 Definition
Cable(1).Ground = 0;
Cable(1).length = FramePosOrig(nFrames)*multiplier + 0.4;
Cable(1).clampPos(1,:) = [0, CableHeight(1), 0];
for i=1:nFrames
    Cable(1).clampPos(i,:) = [FramePosOrig(i), CableHeight(1), 0];
end
Cable(1).refPointPos(1,1) = 0.2;
for i = 1:nFrames-1
    Cable(1).refPointPos(1,i+1) = Cable.refPointPos(1,i) + diffFramePos(i)*multiplier;
end
Cable(1).gripPointsPos = [0:0.02: Cable(1).length]';
Cable(1).clamped = []; 
Cable(1).gripped = [];
Cable(1).configuration.length = [0 Cable(1).length]';
Cable(1).configuration.state = [-0.5 0 0;
                            1.5 0 0];
Cable(1).stiffness = 0.1;


Cable(2).Ground = -0.05;
Cable(2).length = FramePosOrig(nFrames)*multiplier + 0.4;
for i=1:nFrames
    Cable(2).clampPos(i,:) = [FramePosOrig(i), CableHeight(2), 0];
end
Cable(2).refPointPos = Cable(1).refPointPos;
Cable(2).gripPointsPos = [0:0.02: Cable(2).length]';
Cable(2).clamped = []; 
Cable(2).gripped = [];
Cable(2).configuration.length = [0 Cable(2).length]';
Cable(2).configuration.state = [-0.5 0 0;
                            1.5 0 0];
Cable(2).stiffness = 0.1;


Cable(3).Ground = -0.1;
Cable(3).length = FramePosOrig(nFrames)*multiplier + 0.4;
for i=1:nFrames
    Cable(3).clampPos(i,:) = [FramePosOrig(i), CableHeight(3), 0];
end
Cable(3).refPointPos = Cable(1).refPointPos;
Cable(3).gripPointsPos = [0:0.02: Cable(3).length]';
Cable(3).clamped = []; 
Cable(3).gripped = [];
Cable(3).configuration.length = [0 Cable(3).length]';
Cable(3).configuration.state = [-0.5 0 0;
                            1.5 0 0];
Cable(3).stiffness = 0.1;


Cable(4).Ground = -0.15;
Cable(4).length = FramePosOrig(nFrames)*multiplier + 0.4;
for i=1:nFrames
    Cable(4).clampPos(i,:) = [FramePosOrig(i), CableHeight(4), 0];
end
Cable(4).refPointPos = Cable(1).refPointPos;
Cable(4).gripPointsPos = [0:0.02: Cable(4).length]';
Cable(4).clamped = []; 
Cable(4).gripped = [];
Cable(4).configuration.length = [0 Cable(3).length]';
Cable(4).configuration.state = [-0.5 0 0;
                            1.5 0 0];
Cable(4).stiffness = 0.1;


%Define Manipulators

Manipulator(1).position = [0.9 0.2 0];
Manipulator(1).cable = [];
Manipulator(1).grip = [];

Manipulator(2).position = [0.1 0.3 0];
Manipulator(2).cable = [];
Manipulator(2).grip = [];

%Define Interlinks

i=1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 0.4367;
Interlink(i,1).length2 = 0.4367;
Interlink(i,1).linkLength = 0.419+0.145;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 0.8262;
Interlink(i,1).length2 = 0.8262;
Interlink(i,1).linkLength = 0.074 + 0.226;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 2.5123 - 0.15;
Interlink(i,1).length2 = 2.5123 - 0.1;
Interlink(i,1).linkLength = 0.073 + 0.208;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 2.6722;
Interlink(i,1).length2 = 2.6722;
Interlink(i,1).linkLength = 0.089+0.244;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 4;
Interlink(i,1).length1 = 2.6722;
Interlink(i,1).length2 = 2.6722;
Interlink(i,1).linkLength = 0.089+0.295;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 3;
Interlink(i,1).cable2 = 4;
Interlink(i,1).length1 = 2.6722;
Interlink(i,1).length2 = 2.6722;
Interlink(i,1).linkLength = 0.244+0.295;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 4.4727;
Interlink(i,1).length2 = 4.4727;
Interlink(i,1).linkLength = 0.088 + 0.260;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 5.9991;
Interlink(i,1).length2 = 5.9991;
Interlink(i,1).linkLength = 0.093 + 0.254;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 7.1553;
Interlink(i,1).length2 = 7.1553;
Interlink(i,1).linkLength = 0.087 + 0.276;
Interlink(i,1).flag = 0;
i=i+1;


Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 9.2487;
Interlink(i,1).length2 = 9.2487;
Interlink(i,1).linkLength = 0.098 + 0.287;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 9.6958;
Interlink(i,1).length2 = 9.6958;
Interlink(i,1).linkLength = 0.148 + 0.254;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 10.9425;
Interlink(i,1).length2 = 10.9425;
Interlink(i,1).linkLength = 0.083 + 0.199;
Interlink(i,1).flag = 0;
i=i+1;

%Compute the shape of all cables and plot the state
for i = 1:length(Cable)
    selectedCable = Cable(i);
    selectedCable = ComputeCableShape(selectedCable, Manipulator);
    Cable(i) = selectedCable;
end

% Define the StartState and the Action list
StartState.Cable = Cable;
StartState.Manipulator = Manipulator;
StartState.Interlink = Interlink;
ActionList{1,1} = 0;

% Create the StartNode
StartNode.StartState = StartState;
StartNode.ActionList = ActionList;
StartNode.State = StartState;
SystemNode = StartNode;

tic;
[SystemNode] = InterlinkChecker(SystemNode);

ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 1;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 2;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 3;
ReferencePointList(4).CableID = 2;
ReferencePointList(4).RefID = 1;
ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 2;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 3;
ReferencePointList(7).CableID = 3;
ReferencePointList(7).RefID = 1;
ReferencePointList(8).CableID = 3;
ReferencePointList(8).RefID = 2;
ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 3;
ReferencePointList(10).CableID = 4;
ReferencePointList(10).RefID = 1;
ReferencePointList(11).CableID = 4;
ReferencePointList(11).RefID = 2;
ReferencePointList(12).CableID = 4;
ReferencePointList(12).RefID = 3;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);

[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);
SystemNode = OutNode;
%save FullPlan1.mat

%load FullPlan1.mat
ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 6;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 7;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 8;
ReferencePointList(4).CableID = 2;
ReferencePointList(4).RefID = 6;
ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 7;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 8;
ReferencePointList(7).CableID = 3;
ReferencePointList(7).RefID = 6;
ReferencePointList(8).CableID = 3;
ReferencePointList(8).RefID = 7;
ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 8;
ReferencePointList(10).CableID = 4;
ReferencePointList(10).RefID = 6;
ReferencePointList(11).CableID = 4;
ReferencePointList(11).RefID = 7;
ReferencePointList(12).CableID = 4;
ReferencePointList(12).RefID = 8;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);

[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);
SystemNode = OutNode;
save FullPlan2.mat


load FullPlan2.mat
ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 10;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 11;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 12;
ReferencePointList(4).CableID = 2;
ReferencePointList(4).RefID = 10;
ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 11;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 12;
ReferencePointList(7).CableID = 3;
ReferencePointList(7).RefID = 10;
ReferencePointList(8).CableID = 3;
ReferencePointList(8).RefID = 11;
ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 12;
ReferencePointList(10).CableID = 4;
ReferencePointList(10).RefID = 10;
ReferencePointList(11).CableID = 4;
ReferencePointList(11).RefID = 11;
ReferencePointList(12).CableID = 4;
ReferencePointList(12).RefID = 12;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);



[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);
%save FullPlan3.mat


%load FullPlan3.mat
SystemNode = OutNode;
ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 14;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 15;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 16;
ReferencePointList(4).CableID = 2;
ReferencePointList(4).RefID = 14;
ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 15;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 16;
ReferencePointList(7).CableID = 3;
ReferencePointList(7).RefID = 14;
ReferencePointList(8).CableID = 3;
ReferencePointList(8).RefID = 15;
ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 16;
ReferencePointList(10).CableID = 4;
ReferencePointList(10).RefID = 14;
ReferencePointList(11).CableID = 4;
ReferencePointList(11).RefID = 15;
ReferencePointList(12).CableID = 4;
ReferencePointList(12).RefID = 16;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);



[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);
SystemNode = OutNode;
%save FullPlan4.mat



% load OutNodes.mat
SystemNode = OutNode;
ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 18;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 19;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 20;
ReferencePointList(4).CableID = 2;
ReferencePointList(4).RefID = 18;
ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 19;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 20;
ReferencePointList(7).CableID = 3;
ReferencePointList(7).RefID = 18;
ReferencePointList(8).CableID = 3;
ReferencePointList(8).RefID = 19;
ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 20;
ReferencePointList(10).CableID = 4;
ReferencePointList(10).RefID = 18;
ReferencePointList(11).CableID = 4;
ReferencePointList(11).RefID = 19;
ReferencePointList(12).CableID = 4;
ReferencePointList(12).RefID = 20;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);



[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);



% SystemNode = OutNode;
SystemNode = OutNode;
ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 22;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 23;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 24;
ReferencePointList(4).CableID = 1;
ReferencePointList(4).RefID = 25;

ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 22;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 23;
ReferencePointList(7).CableID = 2;
ReferencePointList(7).RefID = 24;
ReferencePointList(8).CableID = 2;
ReferencePointList(8).RefID = 25;

ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 22;
ReferencePointList(10).CableID = 3;
ReferencePointList(10).RefID = 23;
ReferencePointList(11).CableID = 3;
ReferencePointList(11).RefID = 24;
ReferencePointList(12).CableID = 3;
ReferencePointList(12).RefID = 25;

ReferencePointList(13).CableID = 4;
ReferencePointList(13).RefID = 22;
ReferencePointList(14).CableID = 4;
ReferencePointList(14).RefID = 23;
ReferencePointList(15).CableID = 4;
ReferencePointList(15).RefID = 24;
ReferencePointList(16).CableID = 4;
ReferencePointList(16).RefID = 25;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);



[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);
% save OutNodes.mat



% load OutNodes.mat
SystemNode = OutNode;
ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 27;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 28;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 29;
ReferencePointList(4).CableID = 2;
ReferencePointList(4).RefID = 27;
ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 28;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 29;
ReferencePointList(7).CableID = 3;
ReferencePointList(7).RefID = 27;
ReferencePointList(8).CableID = 3;
ReferencePointList(8).RefID = 28;
ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 29;
ReferencePointList(10).CableID = 4;
ReferencePointList(10).RefID = 27;
ReferencePointList(11).CableID = 4;
ReferencePointList(11).RefID = 28;
ReferencePointList(12).CableID = 4;
ReferencePointList(12).RefID = 29;
ReferencePointList(13).CableID = 2;
ReferencePointList(13).RefID = 25;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);



[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);
% save OutNodes.mat

SystemNode = OutNode;
ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 4;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 5;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 9;
ReferencePointList(4).CableID = 1;
ReferencePointList(4).RefID = 13;

ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 4;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 5;
ReferencePointList(7).CableID = 2;
ReferencePointList(7).RefID = 9;
ReferencePointList(8).CableID = 2;
ReferencePointList(8).RefID = 13;

ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 4;
ReferencePointList(10).CableID = 3;
ReferencePointList(10).RefID = 5;
ReferencePointList(11).CableID = 3;
ReferencePointList(11).RefID = 9;
ReferencePointList(12).CableID = 3;
ReferencePointList(12).RefID = 13;

ReferencePointList(13).CableID = 4;
ReferencePointList(13).RefID = 4;
ReferencePointList(14).CableID = 4;
ReferencePointList(14).RefID = 5;
ReferencePointList(15).CableID = 4;
ReferencePointList(15).RefID = 9;
ReferencePointList(16).CableID = 4;
ReferencePointList(16).RefID = 13;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);



[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);



SystemNode = OutNode;
ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 17;
ReferencePointList(2).CableID = 1;
ReferencePointList(2).RefID = 21;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 26;
ReferencePointList(4).CableID = 1;
ReferencePointList(4).RefID = 30;

ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 17;
ReferencePointList(6).CableID = 2;
ReferencePointList(6).RefID = 21;
ReferencePointList(7).CableID = 2;
ReferencePointList(7).RefID = 26;
ReferencePointList(8).CableID = 2;
ReferencePointList(8).RefID = 30;

ReferencePointList(9).CableID = 3;
ReferencePointList(9).RefID = 17;
ReferencePointList(10).CableID = 3;
ReferencePointList(10).RefID = 21;
ReferencePointList(11).CableID = 3;
ReferencePointList(11).RefID = 26;
ReferencePointList(12).CableID = 3;
ReferencePointList(12).RefID = 30;

ReferencePointList(13).CableID = 4;
ReferencePointList(13).RefID = 17;
ReferencePointList(14).CableID = 4;
ReferencePointList(14).RefID = 21;
ReferencePointList(15).CableID = 4;
ReferencePointList(15).RefID = 26;
ReferencePointList(16).CableID = 4;
ReferencePointList(16).RefID = 30;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);



[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);
t=toc;