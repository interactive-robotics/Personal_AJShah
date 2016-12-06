load SystemNode
OutNode = SystemNode;
Tolerance = 0.05;
ReferencePointList(1).CableID = 2;
ReferencePointList(1).RefID = 4;
FreeManipulators = DetermineFreeManipulators(OutNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(OutNode, 0);
[OutNode SuccessFlag] = AlignReferencePointList(OutNode, Tolerance,  ReferencePointList, FreeManipulators, OccupiedManipulators)


ReferencePointList(1).CableID = 2;
ReferencePointList(1).RefID = 6;
FreeManipulators = DetermineFreeManipulators(OutNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(OutNode, 0);
[OutNode SuccessFlag] = AlignReferencePointList(OutNode, Tolerance,  ReferencePointList, FreeManipulators, OccupiedManipulators)


ReferencePointList(1).CableID = 3;
ReferencePointList(1).RefID = 3;
FreeManipulators = DetermineFreeManipulators(OutNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(OutNode, 0);
[OutNode SuccessFlag] = AlignReferencePointList(OutNode, Tolerance,  ReferencePointList, FreeManipulators, OccupiedManipulators)


ReferencePointList(1).CableID = 3;
ReferencePointList(1).RefID = 5;
FreeManipulators = DetermineFreeManipulators(OutNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(OutNode, 0);
[OutNode SuccessFlag] = AlignReferencePointList(OutNode, Tolerance,  ReferencePointList, FreeManipulators, OccupiedManipulators)


ReferencePointList(1).CableID = 3;
ReferencePointList(1).RefID = 6;
FreeManipulators = DetermineFreeManipulators(OutNode, 0);
OccupiedManipulators = DetermineOccupiedManipulators(OutNode, 0);
[OutNode SuccessFlag] = AlignReferencePointList(OutNode, Tolerance,  ReferencePointList, FreeManipulators, OccupiedManipulators)
