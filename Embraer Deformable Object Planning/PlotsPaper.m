load Node.mat
SystemNode = Node;

[SystemNode ParentNode flag] = ReleaseManipulator(SystemNode, 1)
[SystemNode ParentNode flag] = ReleaseManipulator(SystemNode, 2)

[SystemNode GraspNode ParentNode TransitionHandle flag] = AlignRefPoint(SystemNode, 1, 1, 4, 0.05)
target = SystemNode.State.Manipulator(2).position + [0.2 1.2 0];
[SystemNode ParentNode flag] = RepositionManipulator(SystemNode, 2, target)
ClampedCable = 1;
CurrentViolatedInterlinks = ViolatedInterlinks(SystemNode);
[CorrespondingCables CorrespondingCablesStruct] = DetermineCorrespondingCables(SystemNode, CurrentViolatedInterlinks, ClampedCable);
[InterlinkByCableStructure] = ClassifyInterlinkByCables(SystemNode);
[CorrespondingCablesStruct] = SegmentReferencePoints(SystemNode, CorrespondingCablesStruct);
[CorrespondingCablesStruct] = IdentifyRelevantGripPoints(SystemNode, CorrespondingCablesStruct, InterlinkByCableStructure);
nCorrespondingCables = max(size(CorrespondingCablesStruct));
figure(1)
subplot(1,2,1)
PlotStateLargeCorrespondingCable(SystemNode, CorrespondingCablesStruct)
%clf
subplot(,1,2)
PlotStateLargeCorrespondingCableGrip(SystemNode, CorrespondingCablesStruct)