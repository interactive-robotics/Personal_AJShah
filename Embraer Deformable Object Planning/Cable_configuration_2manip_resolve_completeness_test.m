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
Interlink(1,1).length2 = 0.7;
Interlink(1,1).linkLength = 0.2;
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

Interlink(6,1).cable1 = 2;
Interlink(6,1).cable2 = 3;
Interlink(6,1).length1 = 0.7;
Interlink(6,1).length2 = 0.7;
Interlink(6,1).linkLength = 0.3;
Interlink(6,1).flag = 0;

Tolerance = 0.05


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

[SystemNode GraspNode ParentNode TransitionHandle flag] = AlignRefPoint(SystemNode, 1, 1, 2, 0.05)
PlotStateLargeGoal(SystemNode)

% [SystemNode ParentNode flag] = GraspCable(SystemNode, 1, 2, 131);
% [SystemNode ParentNode flag] = ClampCable(SystemNode, 1, 2)
% PlotStateLargeGoal(SystemNode)
% 
% [SystemNode ParentNode flag] = GraspCable(SystemNode, 1, 3, 131)
% [SystemNode ParentNode flag] = ClampCable(SystemNode, 1, 2)
% PlotStateLargeGoal(SystemNode)
% 
% [SystemNode ParentNode flag] = GraspCable(SystemNode, 1, 2, 21)
% [SystemNode ParentNode flag] = ClampCable(SystemNode, 1, 1);
% PlotStateLargeGoal(SystemNode)
% target = SystemNode.State.Manipulator(1).position + [0 1.5 0]
% [SystemNode ParentNode flag] = RepositionManipulator(SystemNode, 1, target)
% PlotStateLargeGoal(SystemNode)

ClampedCable = 1;
ClampingManipulator = 1;
ClampUsed = 2;

%FreeManipulators = [2];

CurrentViolatedInterlinks = ViolatedInterlinks(SystemNode);
nCurrentViolatedInterlinks = max(size(CurrentViolatedInterlinks));

[CorrespondingCables CorrespondingCablesStruct] = DetermineCorrespondingCables(SystemNode, CurrentViolatedInterlinks, ClampedCable);

[InterlinkByCableStructure] = ClassifyInterlinkByCables(SystemNode);

%Given the corresponding cables and the violated interlink information determine the  

[CorrespondingCablesStruct] = SegmentReferencePoints(SystemNode, CorrespondingCablesStruct);

%Segment the rightmost and the leftmost points of the gripping points under
%consideration

[CorrespondingCablesStruct] = IdentifyRelevantGripPoints(SystemNode, CorrespondingCablesStruct, InterlinkByCableStructure);



% [OccupiedManipulators] = DetermineOccupiedManipulators(SystemNode, ClampingManipulator);
% [SystemNode ParentNode flag] = GraspCable(SystemNode, 2, 2, 81);
% [SystemNode] = ResolveInterlinkControlProblem(SystemNode, 2);
% 
% [SystemNode GraspNode ParentNode TransitionHandle flag] = AlignRefPoint(SystemNode, 3, 1, 2, 0.05);
% PlotStateLargeGoal(SystemNode);
% ClampedCable = 3;










%Test suite for interlink resolution

CurrentViolatedInterlinks = ViolatedInterlinks(SystemNode);
nCurrentViolatedInterlinks = max(size(CurrentViolatedInterlinks));
[CorrespondingCables CorrespondingCablesStruct] = DetermineCorrespondingCables(SystemNode, CurrentViolatedInterlinks, ClampedCable);
[InterlinkByCableStructure] = ClassifyInterlinkByCables(SystemNode);
[CorrespondingCablesStruct] = SegmentReferencePoints(SystemNode, CorrespondingCablesStruct);
[CorrespondingCablesStruct] = IdentifyRelevantGripPoints(SystemNode, CorrespondingCablesStruct, InterlinkByCableStructure);
CorrespondingCablesStruct.AssignedManipulator = [];

FreeManipulators = DetermineFreeManipulators(SystemNode, ClampingManipulator);
[OccupiedManipulators] = DetermineOccupiedManipulators(SystemNode, ClampingManipulator);
CablesOriginallyManipulated = DetermineManipulatedCables(OccupiedManipulators);
nCorrespondingCables = max(size(CorrespondingCablesStruct));
CablesUnassigned = [];
for i = 1:nCorrespondingCables
    
    if ~isContain(CablesOriginallyManipulated, CorrespondingCablesStruct(i).CableIndex)
        
        CablesUnassigned = [CablesUnassigned i]; %CablesUnassigned elements refer to the index of the cable in the CorrespondingCables structure
    else
        
        [~, index] = isContain(CablesOriginallyManipulated, CorrespondingCablesStruct(i).CableIndex);
        CorrespondingCablesStruct(i).AssignedManipulator = OccupiedManipulators(index).ManipID;
        
    end
    
end

nCablesUnassigned = max(size(CablesUnassigned));
nFreeManipulators = max(size(FreeManipulators));

if nCablesUnassigned > nFreeManipulators %Interlink resolution is not possible as the number of cables affected is more than the manipulators available
    
    [OutNode ParentNode flag] = TransitionHandle(GraspNode);
    InterlinkResolutionSuccessFlag = 0;
    return; %Exit the function after declaring failure to resolve the interlinks constraint
    
else %Carry out the rest of the function here
    
    %First assign the unassigned cables to the free manipulators
    if nCablesUnassigned > 0 %This is required only if there are any unassigned cables
        for i = 1:nCablesUnassigned
            
            %Assign the manipulator to the correspondingCable indicated by
            %the unassigned cables array
            selectedCorrespondingCable = CorrespondingCablesStruct(CablesUnassigned(i));
            selectedCorrespondingCable.AssignedManipulator = FreeManipulators(i);
            CorrespondingCablesStruct(CablesUnassigned(i)) = selectedCorrespondingCable;
            
        end
    end
    

    SingleStepAlignmentCableID = [];
    SingleStepAlignmentRefID = [];
    SingleStepAlignmentManipID = [];
    RepositionCableID = [CablesOriginallyManipulated];
    
    if CablesUnassigned > 0 %else single step alignment is not possible
    for i = 1:nCablesUnassigned

        selectedCorrespondingCable = CorrespondingCablesStruct(CablesUnassigned(i));
        CableID = selectedCorrespondingCable.CableIndex;
        ManipID = selectedCorrespondingCable.AssignedManipulator;
        SortedReferencePointList = ArrangeReferencePointsByPreference(GraspNode, selectedCorrespondingCable);
        nReferencePoints = max(size(SortedReferencePointList));
        addFlag = 0;
        for j = 1:nReferencePoints

        RefID = SortedReferencePointList(j);
        [tempNode tempGraspNode ParentNode tempTransitionHandle] = AlignRefPoint(SystemNode, CableID, ManipID, RefID, Tolerance);
        FlagList = IsInterlinkViolated(tempNode, selectedCorrespondingCable.ViolatedInterlink);
        if sum(FlagList == 0)
        tempCurrentViolatedInterlinks = ViolatedInterlinks(tempNode);
        if ~isempty(tempCurrentViolatedInterlinks)
            [tempCorrespondingCables tempCorrespondingCablesStruct] = DetermineCorrespondingCables(tempNode, CurrentViolatedInterlinks, ClampedCable);
            ntempCorrespondingCables = max(size(tempCorrespondingCables));
            for k = 1:ntempCorrespondingCables
                Containflag(k) = ~isContain(CablesOriginallyManipulated,tempCorrespondingCables(k));
            end
            if sum(Containflag) == 0
                SingleStepAlignmentCableID = [SingleStepAlignmentCableID CableID];
                SingleStepAlignmentRefID = [SingleStepAlignmentRefID RefID];
                SingleStepAlignmentManipID = [SingleStepAlignmentManipID ManipID];
                addFlag = 1;
                break;
            
            end
        else
            SingleStepAlignmentCableID = [SingleStepAlignmentCableID CableID];
            SingleStepAlignmentRefID = [SingleStepAlignmentRefID RefID];
            SingleStepAlignmentManipID = [SingleStepAlignmentManipID ManipID];
            addFlag = 1;
            break;
        end
        end
        
        end
        
        if addFlag == 0
            RepositionCableID = [RepositionCableID CableID];
        end

    end
    
    if isempty(RepositionCableID) %Only single step resolution has resolved the interlink problem. No need for positioning the cables
        
        %Perform the single step resolution
        [GraspNode, ParentNode, flag] = GraspMultipleRefPoint(GraspNode, SingleStepAlignmentCableID, SingleStepAlignmentManipID, SingleStepAlignmentRefID, Tolerance);
        %PlotStateLargeGoal(GraspNode)
        [GraspNode] = TransitionHandle(GraspNode);
        %PlotStateLargeGoal(GraspNode)
        nSingleStepAlignments = max(size(SingleStepAlignmentCableID))
        for i = 1:nSingleStepAlignments
            
            [GraspNode ParentNode flag] = ClampCableParallel(GraspNode, SingleStepAlignmentManipID(i), SingleStepAlignmentRefID(i));
            
        end
       %Declare Success
       InterlinkResolutionSuccessFlag = 1;
       OutNode = GraspNode;
       return;
    end       
    end
    
    % Now look into respositioning for resolving the interlink constraint
    % through repositioning the other cables that cannot conduct a one step
    % resolution
    
    % First transfer the system node to the state which grasps the clamping
    % cable and the single step resolution cables
    
    if ~isempty(SingleStepAlignmentCableID) % There are possible single step alignments
    [GraspNode ParentNode flag] = GraspMultipleRefPoint(GraspNode, SingleStepAlignmentCableID, SingleStepAlignmentManipID, SingleStepAlignmentRefID, Tolerance);
    
    [SystemNode] = TransitionHandle(GraspNode);
    nSingleStepAlignments = max(size(SingleStepAlignmentCableID));
        for i = 1:nSingleStepAlignments
            
            [SystemNode ParentNode flag] = ClampCableParallel(SystemNode, SingleStepAlignmentManipID(i), SingleStepAlignmentRefID(i));
            
        end
    end
    
    
    
    
    
    
    %At this stage the last Node is the GraspNode which has grasped all the
    %cables for single step alignment. Grasping for reposition must be done
    %parallel to this stage. SystemNode has the clamping cable clamped and
    %all the single stage resolutions completed as well
    
    %Create a new structure of CorrespondingCables that deals only with
    %repositionsing
    
    nRepositionCables = max(size(RepositionCableID));
    RepositionCorrespondingCablesStruct = [];
    for i=1:nCorrespondingCables
        if isContain(RepositionCableID, CorrespondingCablesStruct(i).CableIndex)
            newCorrespondingCablesStruct = CorrespondingCablesStruct(i);
            RepositionCorrespondingCablesStruct = [RepositionCorrespondingCablesStruct newCorrespondingCablesStruct];
        end
    end
    
    %Now the reference points that must be aligned to free up the
    %manipulators must be determined here.
    %This is to be done only if the number of repositioning manipulators is
    %more than the originally manipulated cables
    ReferencePointsToAlignList = [];
    nCablesOriginallyManipulated = max(size(CablesOriginallyManipulated));
    if nCablesOriginallyManipulated < nRepositionCables
    CurrentAlignmentList = [];
    tempFreeManipulators = DetermineFreeManipulators(SystemNode, 0);
    [ReferencePointsToAlignList idealNode] = DetermineReferencePointsToAlign(SystemNode,Tolerance, RepositionCorrespondingCablesStruct, tempFreeManipulators, CurrentAlignmentList);
    end
    
    
    GeometricResolutionExitFlag = 0;
    GeometricResolutionSuccessFlag = 0;
    nRepositionCorrespondingCables = max(size(RepositionCorrespondingCablesStruct));
    for i = 1:nRepositionCorrespondingCables
        SortedGripPointList(i).List = ArrangeGripPointsByPreference(GraspNode, RepositionCorrespondingCablesStruct(i))';
    end
    CableResolveFlag = zeros(nRepositionCorrespondingCables,1);
    
    while GeometricResolutionExitFlag == 0
        tempGraspNode = GraspNode;
        %select from available gripping point for each correspondingcable
        
        %Begin Sampling GripPoints
        for i = 1:nRepositionCorrespondingCables
            if ~isContain(CablesOriginallyManipulated, RepositionCorrespondingCablesStruct(i).CableIndex)
            if ~isempty(SortedGripPointList(i).List)&& CableResolveFlag(i)==0;
                selectedGripPoint(i) = SortedGripPointList(i).List(1);
                SortedGripPointList(i).List = DeleteElement(SortedGripPointList(i).List,1);
                size(SortedGripPointList(i).List)
            end
            end
        end
        % End Sampling Grip Points
        
        %Act to Grasp Cables at selected Grip Points. Begin with GraspNode
        %and add parallel
        for i = 1:nRepositionCorrespondingCables
            if ~isContain(CablesOriginallyManipulated, RepositionCorrespondingCablesStruct(i).CableIndex)
                [tempGraspNode ParentNode flag] = GraspCableParallel(tempGraspNode, RepositionCorrespondingCablesStruct(i).AssignedManipulator, RepositionCorrespondingCablesStruct(i).CableIndex, selectedGripPoint(i));
            end
        end
        [tempSystemNode, ParentNode, flag] = TransitionHandle(tempGraspNode);
        PlotStateLargeGoal(tempSystemNode)
        
        %Compute the repositioning for the manipulators
        [tempSystemNode, tempParentNode, CableResolveFlag] = ResolveGeometricProblem(tempSystemNode, RepositionCorrespondingCablesStruct);
        checkSum = sum(CableResolveFlag);
        
        if checkSum < nRepositionCables
            GeometricResolutionExitFlag = 0; %resample the grip points and start again
        end
        
        if checkSum == nRepositionCables %geometric resolution was successful, now need to align the reference point list and release manipulators 
            newOccupiedManipulators = DetermineOccupiedManipulators(tempSystemNode, 0);
            newFreeManipulators = DetermineFreeManipulators(tempSystemNode, 0);
            [ tempSystemNode, nestedAlignSuccessFlag ] = AlignReferencePointList( tempSystemNode, Tolerance,  ReferencePointsToAlignList, newFreeManipulators, newOccupiedManipulators );
            
            if nestedAlignSuccessFlag == 1
                OutNode = tempSystemNode;
                GeometricResolutionExitFlag = 1;
                GeometricResolutionSuccessFlag = 1;
            else
                GeometricResolutionExitFlag = 0;
                CableResolveFlag = zeros(nRepositionCorrespondingCables,1);
            end
        end
        
        %Check for grip point list empty
        if checkSum < nRepositionCables
            checksum = 0;
            for i=1:nRepositionCorrespondingCables
                if ~isContain(CablesOriginallyManipulated, RepositionCorrespondingCablesStruct(i).CableIndex)
                    checksum = checksum + isempty(SortedGripPointList(i).List);
                end
            end
            if checksum == nRepositionCorrespondingCables-nCablesOriginallyManipulated
                GeometricResolutionExitFlag = 1;
                GeometricResolutionSuccessFlag = 0;
            end
        end
        % End check for grip point  list empty
    end
   
    
    


    
    
    




end


    






















% ViolatedFlagList = IsInterlinkViolated(SystemNode, [1 2 3 4 5]);

% FreeManipulators = DetermineFreeManipulators(SystemNode, 1);
% selectedCorrespondingCable = CorrespondingCablesStruct(1);
% SortedRefPointsList = ArrangeReferencePointsByPreference(SystemNode, selectedCorrespondingCable)
% 
% ReferencePointList = DetermineReferencePointsToAlign(SystemNode, CorrespondingCablesStruct, FreeManipulators, [])
% 



















    






