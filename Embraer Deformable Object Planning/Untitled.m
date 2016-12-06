% Definition of cable structue
%   Cable.length: constant defining the length of the cable

%   Cable.clampPos: n X 3 matrix consisting of the position of the clamps. Index is the
%   clamp number

%   Cable.referencePos: n X 1 vector of the length along the wire for the reference points

%   Cable.gripPos: n X 1 vector of the length along the wire for the
%   gripping points

%   Cable.clamped: n X 2 vector for each row the first element is the
%   length along the wire that is clamped

%   Cable.gripped: n X 2 matrix for each row the first element is the index
%   of the gripping point and second is the index of the manipulator9 on the
%   wire

%   Cable.configuration.length
%   Cable.configuration.state


% Construct the input cable structure for cable 1

Cable.length = 1.8;
Cable.clampPos = [0.1 0.3 0;
                0.4 0.3 0;
                0.7 0.3 0;
                1.0 0.3 0];
Cable.refPointPos = [0.1;0.5;0.9;1.2];
Cable.gripPointsPos = [0:0.1:Cable.length]';
Cable.clamped = [0.6 2]; 
                %1.0 3];
Cable.gripped = [14 1];

Cable.configuration.length = [0 1.5]';
Cable.configuration.state = [0 0 0;
                            1.5 0 0];
Cable.stiffness = 0.01;
Cable.Ground = -0.1;

% Construct the manipulator structure

Manipulator(1).position = [0.9 0.2 0];
Manipulator(1).cable = [1];
Manipulator(1).grip = [14];

Manipulator(2).position = [0.1 0.3 0];
Manipulator(2).cable = [];
Manipulator(2).grip = [];

Cable = ComputeCableShape(Cable, Manipulator);
PlotState(Cable, Manipulator)

% targetPosition = Cable.clampPos(4,:)
% targetPosition(1) = targetPosition(1) - 0.2;
% targetPosition(2) = targetPosition(2)+0.1;
% targetPosition(3) = pi/3;
% target2 = [0.8 0.1 0];
% %[Cable Manipulator] = RepositionManipulator(Cable, Manipulator, 1, targetPosition);
% [Cable Manipulator] = GraspCable(Cable, Manipulator, 2, 1, 4);
% PlotState(Cable, Manipulator)
% [Cable Manipulator] = RepositionManipulator(Cable, Manipulator, 2, [0.2, 0.3 0]);
% PlotState(Cable, Manipulator)
% [Cable Manipulator] = ReleaseManip(Cable, Manipulator, 2);
% [Cable Manipulator] = ClampCable(Cable, Manipulator, 1, 4);
% [Cable Manipulator] = RepositionManipulator(Cable, Manipulator, 1,  [1.0 0.5 0]);
% [Cable Manipulator] = GraspCable(Cable, Manipulator, 2, 1, 11);
% [Cable Manipulator] = ReleaseManip(Cable, Manipulator, 2);
% % [Cable Manipulator] = ClampCable(Cable, Manipulator, 2, 3);
% [Cable Manipulator] = UnclampCable(Cable, Manipulator, 1, 3);
% % axis equal
% PlotState(Cable, Manipulator)

    