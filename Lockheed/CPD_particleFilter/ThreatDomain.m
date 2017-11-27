classdef ThreatDomain < MissionDomain & handle
    
    properties
        ThreatLocations;
        ThreatThreshhold = 1.0;
        ThreatTolerance = 0.5;
        ThreatDetectionThresh = 1.5;
        Predicates;
    end
    
    methods
        
        function SetThreatLocations(NewDomain,ThreatLocations)
            NewDomain.ThreatLocations = ThreatLocations;
        end
        
        
        
        function X = VectorizeState(NewDomain)
            X(1,1) = NewDomain.CurrentState.x;
            X(2,1) = NewDomain.CurrentState.y;
            X(3,1) = NewDomain.CurrentState.theta;
        end
        
        function XDot = StateDerivative(NewDomain,X,Control)
            %Dubins car steering and potential field repulsion for threats
            %within a certain threshhold radius
            ThreatXDot = 0;
            ThreatYDot = 0;
            
            for i=[1:length(NewDomain.ThreatLocations)]
                dist = norm([(X(1) - NewDomain.ThreatLocations(i).x), (X(2) - NewDomain.ThreatLocations(i).y)]);
                if  dist <= NewDomain.ThreatThreshhold
                    ThreatXDot = ThreatXDot + (X(1) - NewDomain.ThreatLocations(i).x)/dist^2;
                    ThreatYDot = ThreatYDot + (X(2) - NewDomain.ThreatLocations(i).y)/dist^2;
                end
            end
            
            XDot(1,1) = NewDomain.Speed*cos(X(3)) + ThreatXDot;
            XDot(2,1) = NewDomain.Speed*sin(X(3)) + ThreatYDot;
            XDot(3,1) = Control;            
        end
        
        function TrajEntry = PropogateState(NewDomain,Control)
            % PropogateState(NewDomain,Control)
            
            % Propogates the state forward by a constant time step with a
            % constant control input
            
            X = NewDomain.VectorizeState();
            [~,y] = ode45(@(t,x)NewDomain.StateDerivative(x,Control),[0 NewDomain.deltaT],X);
            FinalState = y(end,:);
            FinalState(3) = FinalState(3)+normrnd(0,0.05);
            %Update the state of the Domain
            NewDomain.CurrentState.t = NewDomain.CurrentState.t + NewDomain.deltaT;
            NewDomain.CurrentState.x = FinalState(1);
            NewDomain.CurrentState.y = FinalState(2);
            NewDomain.CurrentState.theta = wrapToPi(FinalState(3));
            
            %Add the state to the trajectory
            TrajEntry =  NewDomain.CurrentState;
            TrajEntry.reward = -0.02 - NewDomain.RewardGain*Control^2;
            TrajEntry.control = Control;
            NewDomain.Trajectory = [NewDomain.Trajectory; struct2table(TrajEntry)];
        end
        
        
        
        function Plan(NewDomain)
            nWaypoints = length(NewDomain.Waypoints);
            if nWaypoints == 0
                error('Cannot generate plans with no waypoints');
            else
                currentWaypoint = 1;
                while currentWaypoint <= nWaypoints
                    NewDomain.PropogateState(NewDomain.HeadingControl(currentWaypoint));
                    WaypointError = norm([(NewDomain.Waypoints(currentWaypoint).x - NewDomain.CurrentState.x), (NewDomain.Waypoints(currentWaypoint).y - NewDomain.CurrentState.y)]);
                    
                    %Change waypoint if the current waypoint is achieved
                    if WaypointError < NewDomain.Tolerance
                        currentWaypoint = currentWaypoint+1;
                    else
                    
                        if currentWaypoint <= nWaypoints
                            %Change the waypoint if it is too close to a threat
                            ThreatDist = zeros(length(NewDomain.ThreatLocations),1);
                            for i = [1:length(NewDomain.ThreatLocations)]
                                delta = [(NewDomain.Waypoints(currentWaypoint).x-NewDomain.ThreatLocations(i).x), (NewDomain.Waypoints(currentWaypoint).y-NewDomain.ThreatLocations(i).y)];
                                ThreatDist(i) = norm(delta);                       
                            end
                            [MinThreatDist,~] = min(ThreatDist);

                            try
                            if (WaypointError<= NewDomain.ThreatDetectionThresh) && (MinThreatDist <= NewDomain.ThreatTolerance)
                                currentWaypoint = currentWaypoint+1;
                            end
                            catch
                                WaypointError
                                MinThreatDist
                            end
                        end
                    end
                end
            end
        end
        
        
        
        function PlotDomain(NewDomain)
            PlotDomain@MissionDomain(NewDomain)
            hold on
            
            %Plot the threat locations
            Centers = zeros(length(NewDomain.ThreatLocations),2);
            Radii = zeros(length(NewDomain.ThreatLocations),1);
            for i=[1:length(NewDomain.ThreatLocations)]
                Centers(i,:) = [NewDomain.ThreatLocations(i).x, NewDomain.ThreatLocations(i).y];
                Radii(i) = NewDomain.ThreatTolerance;
            end
            
            viscircles(Centers, Radii, 'Color',  [0.6350    0.0780    0.1840])
            plot(Centers(:,1),Centers(:,2),'o','Color', [0.6350    0.0780    0.1840])
            
        end
        
        function WaypointPredicates = ComputeWaypointPredicates(NewDomain)
             WaypointPredicates = zeros( height(NewDomain.Trajectory), length(NewDomain.Waypoints));
             for i = [1:size(WaypointPredicates,2)]
                 for j = [1:height(NewDomain.Trajectory)]
                     State = NewDomain.Trajectory(j,:);
                     dist = norm([(State.x-NewDomain.Waypoints(i).x),(State.y - NewDomain.Waypoints(i).y)]);
                     WaypointPredicates(j,i) = dist<=NewDomain.Tolerance;
                 end
             end
                 
        end
         
        function ThreatPredicates = ComputeThreatPredicates(NewDomain)
            ThreatPredicates = zeros(height(NewDomain.Trajectory), length(NewDomain.ThreatLocations));
            for i = [1:size(ThreatPredicates,2)]
                for j = [1:size(ThreatPredicates,1)]
                    State = NewDomain.Trajectory(j,:);
                    dist = norm([(State.x - NewDomain.ThreatLocations(i).x), (State.y - NewDomain.ThreatLocations(i).y)]);
                    ThreatPredicates(j,i) = dist<=NewDomain.ThreatTolerance;
                end
            end
        end
        
        
        function PositionalPredicates = ComputePositionalPredicates(NewDomain)
            PositionalPredicates = zeros(height(NewDomain.Trajectory), length(NewDomain.Waypoints));
            for i = [1:size(PositionalPredicates,2)]
                for j = [1:size(PositionalPredicates,1)]
                    %State = NewDomain.Trajectory(j,:);
                    ThreatDist = zeros(length(NewDomain.ThreatLocations),1);
                    for k = [1:length(NewDomain.ThreatLocations)]
                        ThreatDist(i) = norm([(NewDomain.ThreatLocations(k).x-NewDomain.Waypoints(i).x), (NewDomain.ThreatLocations(k).y - NewDomain.Waypoints(i).y)]);
                    end
                    MinThreatDist = min(ThreatDist);
                    
                    PositionalPredicates(j,i) = MinThreatDist <= NewDomain.ThreatTolerance;
                            
                end 
            end
        end
        
        function ComputePredicates(NewDomain)
            WaypointPredicates = NewDomain.ComputeWaypointPredicates();
            ThreatPredicates = NewDomain.ComputeThreatPredicates();
            PositionalPredicates = NewDomain.ComputePositionalPredicates();
            
            OutTable = table();
            OutTable.WaypointPredicates = WaypointPredicates;
            OutTable.ThreatPredicates = ThreatPredicates;
            OutTable.PositionalPredicates = PositionalPredicates;
            NewDomain.Predicates = OutTable;
        end
    end
     
end