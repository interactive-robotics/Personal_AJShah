clear all;

% Cable 1 Definition
Cable.Ground = 0;
Cable.length = 2.2;
Cable.clampPos = [0 0.3 0;
                0.4 0.3 0;
                0.8 0.3 0;
                1.2 0.3 0];
Cable.refPointPos = [0.2;0.8;1.4;2.0];
Cable.gripPointsPos = [0:0.01: Cable.length]';
Cable.clamped = []; 
Cable.gripped = [];
Cable.configuration.length = [0 Cable.length]';
Cable.configuration.state = [-0.3 0 0;
                            1.5 0 0];
Cable.stiffness = 0.1;


% Cable(2) definition
Cable(2).Ground = -0.05;
Cable(2).length = 2.2;
Cable(2).clampPos = [0 0.5 0;
                    0.4 0.5 0;
                    0.8 0.5 0;
                    1.2 0.5 0];
Cable(2).refPointPos = [0.2 0.8 1.4 2.0]';
Cable(2).gripPointsPos = [0:0.01:Cable(2).length]';
Cable(2).clamped = [];
Cable(2).gripped = [];
Cable(2).configuration.length = [0 Cable(2).length]';
Cable(2).configuration.state = [-0.3 0 0;
                            Cable(2).length 0 0];
Cable(2).stiffness = 0.1;

%Define Manipulators

Manipulator(1).position = [0.9 0.2 0];
Manipulator(1).cable = [];
Manipulator(1).grip = [];

Manipulator(2).position = [0.1 0.3 0];
Manipulator(2).cable = [];
Manipulator(2).grip = [];

% Define the interlinking constraints
Interlink(1).cable1 = 1;
Interlink(1).cable2 = 2;
Interlink(1).length1 = 1.1;
Interlink(1).length2 = 1.0;
Interlink(1).linkLength = 0.3;
Interlink(1).flag = 0;

Interlink(2,:).cable1 = 1;
Interlink(2,:).cable2 = 2;
Interlink(2,:).length1 = 1.6;
Interlink(2,:).length2 = 1.5;
Interlink(2,:).linkLength = 0.3;
Interlink(2,:).flag = 0;


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

PlotState_legend(SystemNode)

[SystemNode, ParentNode, flag] = GraspCable(SystemNode, 2, 2, 81)
PlotState_legend(SystemNode)
target = SystemNode.State.Manipulator(2).position + [0 0.6 0];
 %[SystemNode, ParentNode, flag] = ClampCable(SystemNode, 2, 2)
  [SystemNode, ParentNode, flag] = RepositionManipulator(SystemNode, 2, target);


%Select a grasping point 
PlotState_legend(SystemNode)
[SystemNode, ParentNode, flag] = GraspCable(SystemNode, 1, 1, 100) 
PlotState_legend(SystemNode)

ViolatedLinkList = ViolatedInterlinks(SystemNode);

Interlink = SystemNode.State.Interlink;
GraspedCable = 1;
UsedManipulator = 1;

%for each used manipulator. Set up a local control problem with the
%objective of aligning the interlink points. Two parts to it. First
%classify the link end points into Control Points or Desired Locations

nViolatedLinks = size(ViolatedLinkList,1);
ControlPointLinkList = ViolatedLinkList; % The interlinks belonging to the control point
DesiredPos = [];
CurrentPos = [];
ControlPoint = [];
ReferenceLocation = [];


[ControlPoint ReferenceLocation] = ClassifyInterlinks(SystemNode, ViolatedLinkList, UsedManipulator);

decayFactor = 0.1;

[ LocalJacobian ] = CreateJacobian( SystemNode, ControlPoint, UsedManipulator, decayFactor );

%[CurrentPosition DesiredPosition] = getCurrentAndDesiredPos(SystemNode, ControlPoint, ReferenceLocation);


%Control loop

%Create a temporary Node
tempNode = SystemNode;

% 1) Determine the interlink points that are still stretched

CurrentViolatedLinkList = ViolatedInterlinks(tempNode);
nIter = 100;
ManipulatorPositions = zeros(100,3);
iterCount = 1;
resolveFlag = 0;

PlotState(SystemNode)
pause(1)

while (~isempty(CurrentViolatedLinkList) && resolveFlag == 0)
    
    %Generate the current and the desired positions;
    
    [CurrentPosition DesiredPosition] = getCurrentAndDesiredPos(tempNode, ControlPoint, ReferenceLocation);
    
    %Generate the workspace drive command
    
    DesiredRate = DesiredPosition - CurrentPosition;
    
    %Compute the Local Jacobian
    LocalJacobian = CreateJacobian(tempNode, ControlPoint, UsedManipulator, decayFactor);
    
    %Evaluate the movement command
    MotionCommand = pinv(LocalJacobian)*DesiredRate;
    targetManipulatorPosition = tempNode.State.Manipulator(UsedManipulator).position + 0.1*MotionCommand';
    [tempNode ParentNode flag] = RepositionManipulator(SystemNode, UsedManipulator, targetManipulatorPosition);
    PlotState(tempNode)
    pause(1);
    ManipulatorPositions(iterCount,:) = targetManipulatorPosition;
    
    if iterCount >= nIter
        resolveFlag = 1;
    end
    iterCount = iterCount+1;
    CurrentViolatedLinkList = ViolatedInterlinks(tempNode);
end

% [SystemNode ParentNode flag] = RepositionManipulator(SystemNode, UsedManipulator, targetManipulatorPosition);
% PlotState_legend(SystemNode)
% 
% [SystemNode ParentNode flag] = GraspCableParallel(SystemNode, 2, 2, 35);
% PlotState_legend(SystemNode)
% 
% target = SystemNode.State.Manipulator(1).position + [-0.3 0 0];
% [SystemNode ParentNode flag] = RepositionManipulator(SystemNode , 1, target);
% PlotState_legend(SystemNode)
% 
% [SystemNode ParentNode flag] = ClampCableParallel(SystemNode, 2, 1)
% PlotState_legend(SystemNode)




   
    
    
    






