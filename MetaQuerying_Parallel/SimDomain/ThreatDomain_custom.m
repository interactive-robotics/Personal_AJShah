classdef ThreatDomain_custom < ThreatDomain & handle
    
    properties
        WaypointGroups = {};
    end
    
    methods
        function flag =  Plan(NewDomain,WaypointsToVisit)
            nWaypoints = length(WaypointsToVisit);
            if nWaypoints == 0
                error('Cannot generate plans with no waypoints');
            else
                WaypointIndex = 1;
                currentWaypoint = WaypointsToVisit(1);
                
                tic;
                while WaypointIndex <= nWaypoints && toc < 10
                    currentWaypoint = WaypointsToVisit(WaypointIndex);
                    NewDomain.PropogateState(NewDomain.HeadingControl(currentWaypoint));
                    WaypointError = norm([(NewDomain.Waypoints(currentWaypoint).x - NewDomain.CurrentState.x), (NewDomain.Waypoints(currentWaypoint).y - NewDomain.CurrentState.y)]);
                    
                    %Change waypoint if the current waypoint is achieved
                    if WaypointError < NewDomain.Tolerance
                        WaypointIndex = WaypointIndex+1;
                        %currentWaypoint = WaypointsToVisit(WaypointIndex);
                    else
                    
                        if WaypointIndex <= nWaypoints
                            %Change the waypoint if it is too close to a threat
                            ThreatDist = zeros(length(NewDomain.ThreatLocations),1);
                            for i = [1:length(NewDomain.ThreatLocations)]
                                delta = [(NewDomain.Waypoints(currentWaypoint).x-NewDomain.ThreatLocations(i).x), (NewDomain.Waypoints(currentWaypoint).y-NewDomain.ThreatLocations(i).y)];
                                ThreatDist(i) = norm(delta);                       
                            end
                            [MinThreatDist,~] = min(ThreatDist);

                            try
                            if (WaypointError<= NewDomain.ThreatDetectionThresh) && (MinThreatDist <= NewDomain.ThreatTolerance)
                                WaypointIndex = WaypointIndex+1;
                                
                            end
                            catch
                                WaypointError;
                                MinThreatDist;
                            end
                        end
                    end
                end
                    if WaypointIndex <= nWaypoints
                        flag = 0;
                    else
                        flag = 1;
                    end
            end
        end
        
        
        function FullFlag = PlanFull(NewDomain)
            FullFlag=1;
            nGroups = length(NewDomain.WaypointGroups)
            GroupOrder = randperm(nGroups);
            for i = 1:nGroups
                flag = NewDomain.Plan(NewDomain.WaypointGroups{GroupOrder(i)});
                if flag == 0
                    FullFlag = 0;
                    break;
                end
            end
        end
        
    end
    
end
