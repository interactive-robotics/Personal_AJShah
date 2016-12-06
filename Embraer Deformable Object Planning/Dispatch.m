% This script dispatches the action sequence encoded in the Action list to
% transfer the system from the start state to the final state

%load EmbraerPlan2.mat
SystemNode = OutNode;

StartState = SystemNode.StartState;
ActionList{1,1} = 0;
StartNode.StartState = StartState;
StartNode.State = StartState;
StartNode.ActionList = ActionList;

NodeActionList = SystemNode.ActionList;

SystemNodeHistory = StartNode;
for i = 2:length(NodeActionList)
    
    currentNode = SystemNodeHistory(i-1);
    CurrentActionSet = NodeActionList{i,1};
    
    n_currentActions = size(CurrentActionSet,2);
    Node = currentNode;
    for j = 1:n_currentActions
        
        
        action = CurrentActionSet{1,j};
        
        Node = action(Node);
        %PlotState(Node)
    end
    
    PlotState(Node);
    filename = sprintf('image%i.jpg' , i);
    fig = gcf;
    fig.PaperUnits = 'inches';
    fig.PaperPositionMode = 'manual';
    fig.PaperPosition = [0 0 32 18];
    saveas(gcf,filename);
    
    SystemNodeHistory(i,1).StartState = Node.StartState;
    SystemNodeHistory(i,1).ActionList = ActionList;
    SystemNodeHistory(i,1).State = Node.State;
   pause(0.5);
end