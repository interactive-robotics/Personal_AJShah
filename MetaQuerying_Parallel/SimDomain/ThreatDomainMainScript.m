close all
%Test script for class constructor

nRuns = 10;

for i=[11:30]
[NewDomain, Predicates] = RunDomain(i);
end

%[NewDomain, Predicates] = RunDomain(1);
%[NewDomain, Predicates] = RunThreatDomainViolation(1);
%[NewDomain, Predicates] = RunThreatDomainLazy(1);

% for i = [1:2]
%     
% Waypoints = SampleWaypoints(-5,5,-5,5,5);
% Threats = SampleThreats(-5,5,0,5,5);
% [NewDomain, Predicates] = RunDomainCustom(i, Waypoints, Threats, [1:5])
% %[NewDOmain,Predicates] = RunDomainCustom(2, Waypoints, Threats, [1,3,4,5])
% end



function [NewDomain,Predicates_encoded] = RunDomain(i)
    NewDomain = ThreatDomain();
    
    %Only waypoints no threats

    %Generate the start state randomly in a region
    StartState.x = (-3 + 5)*rand(1,1) -5;
    StartState.y = (-1 + 2)*rand(1,1) -2;
    StartState.theta = 2*pi*rand(1,1) -pi;
    NewDomain.SetStartState(StartState);

    %Generate Waypoints
    Waypoint = struct('x',{},'y',{});
    Waypoint(1).x = 2;
    Waypoint(1).y = 1;

    Waypoint(2).x = 1;
    Waypoint(2).y = 2;

    Waypoint(3).x = 1;
    Waypoint(3).y = 4;

    Waypoint(4).x = -3;
    Waypoint(4).y = 0;

    NewDomain.SetWaypoints(Waypoint);

    %Generate Threat locations
    
    %NewDomain.ThreatLocations = ThreatLocations;
    NewDomain.Plan()

    NewDomain.ComputePredicates();
    NewDomain.PlotDomain()
    imgname = sprintf('Traj_%i.png',i);
    saveas(gcf,strcat('NoThreatData/',imgname));
    close all
    
    Predicates.WaypointPredicates = NewDomain.Predicates.WaypointPredicates';
    %Predicates.ThreatPredicates = NewDomain.Predicates.ThreatPredicates';
    Predicates.PositionPredicates = zeros(size(Predicates.WaypointPredicates));
    
    Predicates_encoded = jsonencode(Predicates);
    filename = sprintf('Predicates_%i.json',i);
    fid = fopen(strcat('NoThreatData/',filename),'w');
    fprintf(fid, Predicates_encoded);
    fclose(fid);
    %Predicates_encoded = 1;
end



function [NewDomain,Predicates_encoded] = RunThreatDomain(i)
    NewDomain = ThreatDomain();

    %Generate the start state randomly in a region
    StartState.x = (-3 + 5)*rand(1,1) -5;
    StartState.y = (-1 + 2)*rand(1,1) -2;
    StartState.theta = 2*pi*rand(1,1) -pi;
    NewDomain.SetStartState(StartState);

    %Generate Waypoints
    Waypoint = struct('x',{},'y',{});
    Waypoint(1).x = 2;
    Waypoint(1).y = 1;

    Waypoint(2).x = 1;
    Waypoint(2).y = 2;

    Waypoint(3).x = 1;
    Waypoint(3).y = 4;

    Waypoint(4).x = -3;
    Waypoint(4).y = 0;

    NewDomain.SetWaypoints(Waypoint);

    %Generate Threat locations
    NewDomain.AddRandomThreats(3,0,5,0,5);
    NewDomain.AddRandomThreats(2,-5,0,0,5);

    %NewDomain.ThreatLocations = ThreatLocations;
    NewDomain.Plan()

    NewDomain.ComputePredicates();
    NewDomain.PlotDomain()
    imgname = sprintf('Traj_%i.png',i);
    saveas(gcf, strcat('ThreatData/',imgname));
    close all;
    
    Predicates.WaypointPredicates = NewDomain.Predicates.WaypointPredicates';
    Predicates.ThreatPredicates = NewDomain.Predicates.ThreatPredicates';
    Predicates.PositionPredicates = NewDomain.Predicates.PositionalPredicates';
    
    Predicates_encoded = jsonencode(Predicates);
    filename = sprintf('Predicates_%i.json',i);
    fid = fopen(strcat('ThreatData/',filename),'w');
    fprintf(fid, Predicates_encoded);
    fclose(fid);
    %Predicates_encoded = 1;
end




function [NewDomain,Predicates_encoded] = RunThreatDomainViolation(i)
    NewDomain = ThreatDomain();
    
    %Only waypoints no threats

    %Generate the start state randomly in a region
    StartState.x = (-3 + 5)*rand(1,1) -5;
    StartState.y = (-1 + 2)*rand(1,1) -2;
    StartState.theta = 2*pi*rand(1,1) -pi;
    NewDomain.SetStartState(StartState);

    %Generate Waypoints
    Waypoint = struct('x',{},'y',{});
    Waypoint(1).x = 2;
    Waypoint(1).y = 1;

    Waypoint(2).x = 1;
    Waypoint(2).y = 2;

    Waypoint(3).x = 1;
    Waypoint(3).y = 4;

    Waypoint(4).x = -3;
    Waypoint(4).y = 0;

    NewDomain.SetWaypoints(Waypoint);

    %Generate Threat locations
    
    %NewDomain.ThreatLocations = ThreatLocations;
    NewDomain.Plan()
    ThreatLocations(1).x = 2;
    ThreatLocations(1).y = 1;
    NewDomain.ThreatLocations = ThreatLocations;

    NewDomain.ComputePredicates();
    NewDomain.ComputePredicates();
    NewDomain.PlotDomain()
    imgname = sprintf('Traj_%i.png',i);
    saveas(gcf,strcat('ThreatViolation/',imgname));
    close all
    
    Predicates.WaypointPredicates = NewDomain.Predicates.WaypointPredicates';
    Predicates.ThreatPredicates = NewDomain.Predicates.ThreatPredicates';
    Predicates.PositionPredicates = NewDomain.Predicates.PositionalPredicates';
    
    Predicates_encoded = jsonencode(Predicates);
    filename = sprintf('Predicates_%i.json',i);
    fid = fopen(strcat('ThreatViolation/',filename),'w');
    fprintf(fid, Predicates_encoded);
    fclose(fid);
    %Predicates_encoded = 1;
end

function [NewDomain,Predicates_encoded] = RunThreatDomainLazy(i)
    NewDomain = ThreatDomain();

    %Generate the start state randomly in a region
    StartState.x = (-3 + 5)*rand(1,1) -5;
    StartState.y = (-1 + 2)*rand(1,1) -2;
    StartState.theta = 2*pi*rand(1,1) -pi;
    NewDomain.SetStartState(StartState);

    %Generate Waypoints
    Waypoint = struct('x',{},'y',{});
    Waypoint(1).x = 2;
    Waypoint(1).y = 1;

    Waypoint(2).x = 1;
    Waypoint(2).y = 2;

    %Waypoint(3).x = 1;
    %Waypoint(3).y = 4;

    %Waypoint(4).x = -3;
    %Waypoint(4).y = 0;

    NewDomain.SetWaypoints(Waypoint);

    %Generate Threat locations
    ThreatLocations(1).x = -3;
    ThreatLocations(1).y = 0;
    
    NewDomain.ThreatLocations = ThreatLocations;
    
    
    %NewDomain.ThreatLocations = ThreatLocations;
    NewDomain.Plan()

    NewDomain.ComputePredicates();
    
    %Add the other waypoints
    Waypoint(3).x = 1;
    Waypoint(3).y = 4;

    Waypoint(4).x = -3;
    Waypoint(4).y = 0;
    NewDomain.SetWaypoints(Waypoint)
    
    
    NewDomain.PlotDomain()
    NewDomain.ComputePredicates();
    imgname = sprintf('Traj_%i.png',i);
    saveas(gcf, strcat('LazyExecution/',imgname));
    close all;
    
    Predicates.WaypointPredicates = NewDomain.Predicates.WaypointPredicates';
    Predicates.ThreatPredicates = NewDomain.Predicates.ThreatPredicates';
    Predicates.PositionPredicates = NewDomain.Predicates.PositionalPredicates';
    
    Predicates_encoded = jsonencode(Predicates);
    filename = sprintf('Predicates_%i.json',i);
    fid = fopen(strcat('LazyExecution/',filename),'w');
    fprintf(fid, Predicates_encoded);
    fclose(fid);
    %Predicates_encoded = 1;
end












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


function [NewDomain, Predicates] = RunDomainCustom(i, Waypoints, Threats, WaypointsToVisit)
    
    NewDomain = ThreatDomain();
    NewDomain.Waypoints = Waypoints(WaypointsToVisit);
    NewDomain.ThreatLocations = Threats;
    
    NewDomain.Plan;
    
    NewDomain.Waypoints = Waypoints;
    NewDomain.ThreatLocations = Threats;
    NewDomain.ComputePredicates;
    
    Predicates.WaypointPredicates = NewDomain.Predicates.WaypointPredicates';
    Predicates.ThreatPredicates = NewDomain.Predicates.ThreatPredicates';
    Predicates.PositionPredicates = NewDomain.Predicates.PositionalPredicates';
    
    NewDomain.PlotDomain();
    imgname = sprintf('exampleTrajs/Traj_%i.png',i);
    imgname
    saveas(gcf, imgname);
    close all;
    
    Predicates_encoded = jsonencode(Predicates);
    filename = sprintf('exampleTrajs/Predicates_%i.json',i);
    fid = fopen(filename,'w');
    fprintf(fid, Predicates_encoded);
    fclose(fid);
    
    
end
