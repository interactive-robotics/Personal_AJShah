clear all;

% Cable 1 Definition
Cable(1).Ground = 0;
Cable(1).length = 5.9;
Cable(1).clampPos = [0 0.5 0;
                1 0.5 0;
                2 0.5 0;
                3 0.5 0
                4 0.5 0
                5 0.5 0];
Cable(1).refPointPos = [0.2:1.1:5.7];
Cable(1).gripPointsPos = [0:0.01: Cable(1).length]';
Cable(1).clamped = []; 
Cable(1).gripped = [];
Cable(1).configuration.length = [0 Cable(1).length]';
Cable(1).configuration.state = [-0.5 0 0;
                            1.5 0 0];
Cable(1).stiffness = 0.1;


Cable(2).Ground = -0.05;
Cable(2).length = 5.9;
Cable(2).clampPos = [0 0.7 0;
                1 0.7 0;
                2 0.7 0;
                3 0.7 0
                4 0.7 0
                5 0.7 0];
Cable(2).refPointPos = [0.2:1.1:5.7];
Cable(2).gripPointsPos = [0:0.01: Cable(2).length]';
Cable(2).clamped = []; 
Cable(2).gripped = [];
Cable(2).configuration.length = [0 Cable(2).length]';
Cable(2).configuration.state = [-0.5 0 0;
                            1.5 0 0];
Cable(2).stiffness = 0.1;


Cable(3).Ground = -0.1;
Cable(3).length = 5.9;
Cable(3).clampPos = [0 0.9 0;
                1 0.9 0;
                2 0.9 0;
                3 0.9 0
                4 0.9 0
                5 0.9 0];
Cable(3).refPointPos = [0.2:1.1:5.7];
Cable(3).gripPointsPos = [0:0.01: Cable(3).length]';
Cable(3).clamped = []; 
Cable(3).gripped = [];
Cable(3).configuration.length = [0 Cable(3).length]';
Cable(3).configuration.state = [-0.5 0 0;
                            1.5 0 0];
Cable(3).stiffness = 0.1;


%Define Manipulators

Manipulator(1).position = [0.9 0.2 0];
Manipulator(1).cable = [];
Manipulator(1).grip = [];

Manipulator(2).position = [0.1 0.3 0];
Manipulator(2).cable = [];
Manipulator(2).grip = [];



% Define the interlinking constraints
Interlink(1,1).cable1 = 1;
Interlink(1,1).cable2 = 2;
Interlink(1,1).length1 = 0.7;
Interlink(1,1).length2 = 0.9;
Interlink(1,1).linkLength = 0.35;
Interlink(1,1).flag = 0;

Interlink(2,1).cable1 = 1;
Interlink(2,1).cable2 = 2;
Interlink(2,1).length1 = 2.9;
Interlink(2,1).length2 = 2.9;
Interlink(2,1).linkLength = 0.3;
Interlink(2,1).flag = 0;

Interlink(3,1).cable1 = 1;
Interlink(3,1).cable2 = 2;
Interlink(3,1).length1 = 5.1;
Interlink(3,1).length2 = 5.1;
Interlink(3,1).linkLength = 0.3;
Interlink(3,1).flag = 0;

Interlink(4,1).cable1 = 2;
Interlink(4,1).cable2 = 3;
Interlink(4,1).length1 = 1.7;
Interlink(4,1).length2 = 1.7;
Interlink(4,1).linkLength = 0.3;
Interlink(4,1).flag = 0;

Interlink(5,1).cable1 = 2;
Interlink(5,1).cable2 = 3;
Interlink(5,1).length1 = 3.9;
Interlink(5,1).length2 = 3.9;
Interlink(5,1).linkLength = 0.3;
Interlink(5,1).flag = 0;




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

%PlotStateLargeGoal(SystemNode)

[SystemNode ParentNode flag] = GraspCable(SystemNode, 1, 1, 21);
PlotStateLargeGoal(SystemNode);
[SystemNode ParentNode flag] = ClampCable(SystemNode, 1, 1);
PlotStateLargeGoal(SystemNode);
% [SystemNode ParentNode flag] = UnclampCable(SystemNode, 1, 1)

[SystemNode GraspNode ParentNode TransitionHandle, flag] = AlignRefPoint(SystemNode, 1, 1, 2, 0.05)
PlotStateLargeGoal(SystemNode);

[SystemNode, GraspNode, ParentNode, TransitionHandle] = AlignRefPointParallel(GraspNode, TransitionHandle, 2, 2, 1, 0.02);
PlotStateLargeGoal(SystemNode)





























% ViolatedFlagList = IsInterlinkViolated(SystemNode, [1 2 3 4 5]);

% FreeManipulators = DetermineFreeManipulators(SystemNode, 1);
% selectedCorrespondingCable = CorrespondingCablesStruct(1);
% SortedRefPointsList = ArrangeReferencePointsByPreference(SystemNode, selectedCorrespondingCable)
% 
% ReferencePointList = DetermineReferencePointsToAlign(SystemNode, CorrespondingCablesStruct, FreeManipulators, [])
% 



















    






