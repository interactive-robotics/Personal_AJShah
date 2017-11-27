close all
%Test script for class constructor
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
ThreatLocations = struct('x',{},'y',{});
ThreatLocations(1).x = 0;
ThreatLocations(1).y = 0;

ThreatLocations(2).x = -3;
ThreatLocations(2).y = 0.25;

NewDomain.ThreatLocations = ThreatLocations;
NewDomain.Plan()

NewDomain.ComputePredicates();
NewDomain.PlotDomain()