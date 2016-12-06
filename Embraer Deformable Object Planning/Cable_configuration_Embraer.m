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



% Define the interlinking constraints

v;

Interlink(2,1).cable1 = 3;
Interlink(2,1).cable2 = 4;
Interlink(2,1).length1 = 6.7582 + 0.10;
Interlink(2,1).length2 = 6.7582 + 0.05;
Interlink(2,1).linkLength = 0.10 + 0.23;
Interlink(2,1).flag = 0;

Interlink(3,1).cable1 = 2;
Interlink(3,1).cable2 = 3;
Interlink(3,1).length1 = 6.7582 + 0.05;
Interlink(3,1).length2 = 6.7582 + 0.10;
Interlink(3,1).linkLength = 0.10 + 0.38;
Interlink(3,1).flag = 0;

Interlink(4,1).cable1 = 2;
Interlink(4,1).cable2 = 4;
Interlink(4,1).length1 = 6.7582 + 0.05;
Interlink(4,1).length2 = 6.7582 + 0.05;
Interlink(4,1).linkLength = 0.38 + 0.23;
Interlink(4,1).flag = 0;

Interlink(5,1).cable1 = 3;
Interlink(5,1).cable2 = 4;
Interlink(5,1).length1 = 6.7582 + 0.10;
Interlink(5,1).length2 = 6.7582 + 0.05;
Interlink(5,1).linkLength = 0.10 + 0.23;
Interlink(5,1).flag = 0;

i=6;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 8.899 - 0.15;
Interlink(i,1).length2 = 8.899 - 0.05;
Interlink(i,1).linkLength = 0.26 + 0.12;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 4;
Interlink(i,1).length1 = 8.899 - 0.15;
Interlink(i,1).length2 = 8.899 - 0.15;
Interlink(i,1).linkLength = 0.26 + 0.12;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 3;
Interlink(i,1).cable2 = 4;
Interlink(i,1).length1 = 8.899 - 0.05;
Interlink(i,1).length2 = 8.899 - 0.15;
Interlink(i,1).linkLength = 0.26 + 0.26;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 1;
Interlink(i,1).cable2 = 2;
Interlink(i,1).length1 = 10.5927 - 0.10;
Interlink(i,1).length2 = 10.5927 + 0.07;
Interlink(i,1).linkLength = 0.20 + 0.11;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 1;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 10.5927 - 0.10;
Interlink(i,1).length2 = 10.5927 + 0.02;
Interlink(i,1).linkLength = 0.2 + 0.3;
Interlink(i,1).flag = 0;
i=i+1;

Interlink(i,1).cable1 = 2;
Interlink(i,1).cable2 = 3;
Interlink(i,1).length1 = 10.5927 + 0.07;
Interlink(i,1).length2 = 10.5927 + 0.02;
Interlink(i,1).linkLength = 0.11 + 0.3;
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


[SystemNode] = InterlinkChecker(SystemNode);

% [SystemNode ParentNode Flag] = AlignRefPoint(SystemNode, 4, 1, 17, 0.05)


% ReferencePointList(1).CableID = 3;
% ReferencePointList(1).RefID = 17;
% FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
% OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);
% 
% [OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);


ReferencePointList(1).CableID = 4;
ReferencePointList(1).RefID = 21;
ReferencePointList(2).CableID = 3;
ReferencePointList(2).RefID = 21;
ReferencePointList(3).CableID = 2;
ReferencePointList(3).RefID = 21;
ReferencePointList(4).CableID = 2;
ReferencePointList(4).RefID = 22;
ReferencePointList(5).CableID = 3;
ReferencePointList(5).RefID = 22;
ReferencePointList(6).CableID = 4;
ReferencePointList(6).RefID = 22;
FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);

[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);

SystemNode = OutNode;
ReferencePointList(1).CableID = 3;
ReferencePointList(1).RefID = 26;
ReferencePointList(2).CableID = 2;
ReferencePointList(2).RefID = 26;
ReferencePointList(3).CableID = 1;
ReferencePointList(3).RefID = 26;
ReferencePointList(4).CableID = 1;
ReferencePointList(4).RefID = 27;
ReferencePointList(5).CableID = 2;
ReferencePointList(5).RefID = 27;
ReferencePointList(6).CableID = 3;
ReferencePointList(6).RefID = 27;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);

[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);

SystemNode = OutNode;
ReferencePointList(1).CableID = 4;
ReferencePointList(1).RefID = 17;
ReferencePointList(2).CableID = 3;
ReferencePointList(2).RefID = 17;
ReferencePointList(3).CableID = 2;
ReferencePointList(3).RefID = 17;
ReferencePointList(4).CableID = 2;
ReferencePointList(4).RefID = 18;
ReferencePointList(5).CableID = 3;
ReferencePointList(5).RefID = 18;
ReferencePointList(6).CableID = 4;
ReferencePointList(6).RefID = 18;

FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);

[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, 0.05,  ReferencePointList, FreeManipulators, OccupiedManipulators);
