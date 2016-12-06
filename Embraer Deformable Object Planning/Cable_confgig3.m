clear all;

% Cable 1 Definition
Cable.Ground = 0;
Cable.length = 2.2;
 Cable.clampPos = [0 0.3 0];
%                 0.4 0.3 0;
%                 0.8 0.3 0;
%                 1.2 0.3 0];
Cable.refPointPos = [0.2];
Cable.gripPointsPos = [0:0.05: Cable.length]';
Cable.clamped = []; 
Cable.gripped = [];
Cable.configuration.length = [0 Cable.length]';
Cable.configuration.state = [-0.3 0 0;
                            1.5 0 0];
Cable.stiffness = 0.1;


% % Cable(2) definition
% Cable(2).Ground = -0.05;
% Cable(2).length = 2.2;
% Cable(2).clampPos = [0 0.4 0;
%                     0.5 0.4 0;
%                     1.0 0.4 0;
%                     1.5 0.4 0];
% Cable(2).refPointPos = [0.2 0.8 1.4 2.0]';
% Cable(2).gripPointsPos = [0:0.05:Cable(2).length]';
% Cable(2).clamped = [];
% Cable(2).gripped = [];
% Cable(2).configuration.length = [0 Cable(2).length]';
% Cable(2).configuration.state = [-0.3 0 0;
%                             Cable(2).length 0 0];
% Cable(2).stiffness = 0.1;
% 
%Define Manipulators

Manipulator(1).position = [0.9 0.2 0];
Manipulator(1).cable = [];
Manipulator(1).grip = [];

Manipulator(2).position = [0.1 0.3 0];
Manipulator(2).cable = [];
Manipulator(2).grip = [];
% 
% % Define the interlinking constraints
Interlink = []
% Interlink(1).cable1 = 1;
% Interlink(1).cable2 = 2;
% Interlink(1).length1 = 1.1;
% Interlink(1).length2 = 1.0;
% Interlink(1).linkLength = 0.3;
% Interlink(1).flag = 0;
% 
% Interlink(2).cable1 = 1;
% Interlink(2).cable2 = 2;
% Interlink(2).length1 = 1.6;
% Interlink(2).length2 = 1.5;
% Interlink(2).linkLength = 0.5;
% Interlink(2).flag = 0;


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
PlotState(SystemNode)

% Initialte the input structure
SystemNode = GraspCable(SystemNode, 1, 1, 24);
PlotState(SystemNode);
ManipPos = SystemNode.State.Manipulator(1).position;
target = ManipPos + [0 0.3 0];
SystemNode = RepositionManipulator(SystemNode, 1, target);
PlotState_legend(SystemNode)

