
load CableConfig.mat

ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 1;
FreeManipulators = DetermineFreeManipulators(SystemNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(SystemNode, 0);
[OutNode SuccessFlag] = AlignReferencePointList(SystemNode, Tolerance,  ReferencePointList, FreeManipulators, OccupiedManipulators)





load SysNode1.mat
OutNode = SystemNode;
Tolerance = 0.05;

ReferencePointList(1).CableID = 1;
ReferencePointList(1).RefID = 6;
FreeManipulators = DetermineFreeManipulators(OutNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(OutNode, 0);
[OutNode SuccessFlag] = AlignReferencePointList(OutNode, Tolerance,  ReferencePointList, FreeManipulators, OccupiedManipulators)