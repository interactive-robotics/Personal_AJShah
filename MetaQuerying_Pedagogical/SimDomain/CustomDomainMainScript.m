nDemos = 50;
DomainID = 3;

%Generate the waypoints
Waypoint = struct('x',{},'y',{});
Waypoint(1).x = 2;
Waypoint(1).y = 1;

Waypoint(2).x = 1;
Waypoint(2).y = 2;

Waypoint(3).x = 2;
Waypoint(3).y = 4;

Waypoint(4).x = -3;
Waypoint(4).y = 0;

Waypoint(5).x = -4;
Waypoint(5).y = 2;

%     Waypoint = struct('x',{},'y',{});
%     Waypoint(1).x = 2;
%     Waypoint(1).y = 1;
% 
%     Waypoint(2).x = 1;
%     Waypoint(2).y = 2;
% 
%     Waypoint(3).x = 1;
%     Waypoint(3).y = 4;
% 
%     Waypoint(4).x = -3;
%     Waypoint(4).y = 0;

%Define task hierarchy
WaypointGroups = {[1,3,5],[2],[4]}

% WaypointGroups_Possible = cell(0,1);
% WaypointGroups_Possible{1} = {[1,5,3],[2],[4]};
% 
% WaypointGroups_Possible{2} = {[1,3,5],[2]};
% WaypointGroups_Possible{3} = {[1,2,3],[5],[4]};
% WaypointGroups_Possible{4} = {[1,5],[4],[3]};
% WaypointGroups_Possible{5} = {[3,1,5]};


%WaypointGroups = {[3,1,4,2]};


nThreats = 0;

foldername = sprintf('CustomDomain%i',DomainID)

if ~exist (sprintf(foldername,DomainID))
    mkdir(sprintf(foldername, DomainID))
end

save(strcat(foldername,'/','DomainData.mat'), 'Waypoint', 'nThreats', 'WaypointGroups');

for i=1:nDemos
    i
    GrpID = randi([1 5]);
    %WaypointGroups = WaypointGroups_Possible{GrpID};
    WaypointGroups
    [NewDomain, PredicatesEncoded] = RunCustomDomain(i,1, Waypoint, nThreats, WaypointGroups, foldername);
end

%% Helper functions


function Waypoints = SampleWaypoints(XMin, XMax, YMin, YMax, n)
Waypoints = [];
for i = 1:n
    
    NewWaypoint.x = XMin + (XMax - XMin)*rand(1,1);
    NewWaypoint.y = YMin + (YMax - YMin)*rand(1,1);
    Waypoints = [Waypoints; NewWaypoint];    
end
end

function Threats = SampleThreats(XMin, XMax, YMin, YMax, n)
Threats = [];
for i=1:n
    
    NewThreat.x = XMin + (XMax - XMin)*rand(1,1);
    NewThreat.y = YMin + (YMax - YMin)*rand(1,1);
    Threats = [Threats; NewThreat];
end
end

function [NewDomain PredicatesEncoded] = RunCustomDomain(i, DomainID, Waypoint, nThreats, WaypointGroups, foldername)

    flag = 0;
    while flag==0
    

    NewDomain = ThreatDomain_custom();

    %Generate the start state randomly in a region
    StartState.x = (-3 + 5)*rand(1,1) -5;
    StartState.y = (-1 + 2)*rand(1,1) -2;
    StartState.theta = 2*pi*rand(1,1) -pi;
    NewDomain.SetStartState(StartState);
    
    nWaypoints = length(Waypoint);

    %Generate Threats

    Threats = SampleThreats(-4,4, -4, 4, nThreats);

    NewDomain.Waypoints = Waypoint;
    NewDomain.ThreatLocations = Threats;

    
    NewDomain.WaypointGroups = WaypointGroups;
    
    flag = NewDomain.PlanFull();
    end
    NewDomain.PlotDomain()


    NewDomain.ComputePredicates();
    Predicates.WaypointPredicates = NewDomain.Predicates.WaypointPredicates';
    Predicates.ThreatPredicates = NewDomain.Predicates.ThreatPredicates';
    Predicates.PositionPredicates = NewDomain.Predicates.PositionalPredicates';
    PredicatesEncoded = jsonencode(Predicates);
    
    imgname = sprintf('Traj_%i.png',i);
    saveas(gcf, strcat(foldername, '/' ,imgname));
    close all;
    
    
    filename = sprintf('Predicates_%i.json',i);
    fid = fopen(strcat(foldername,'/',filename),'w');
    fprintf(fid, PredicatesEncoded);
    fclose(fid);
    
    dataFilename = sprintf('Data_%i.mat',i);
    Trajectory = NewDomain.Trajectory;
    save(strcat(foldername,'/',dataFilename),'Trajectory');
end


