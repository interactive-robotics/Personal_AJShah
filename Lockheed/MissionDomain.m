% This script defines the scenario for flight including start location
% current state and goal location and waypoints. 

classdef MissionDomain < handle
    properties
        %Set Domain bounds
        Bounds;
        
        %The object forward speed
        Speed;
               
        %Set start state
        StartState;
        
        %Waypoints
        Waypoints;
        
        %Set position error tolerance
        Tolerance = 0.2;
        
        %Current State
        CurrentState;
        
        %Simulation step time
        deltaT = 0.1;
        
        %trajectory
        Trajectory
        
        %Reward gains
        RewardGain;
        
        
    end
    
    methods
        %Write the constructor for a new domain object. Define methods for
        %taking in set values or for initializing with defaults
        
        function NewDomain = MissionDomain(Bounds,StartState,Waypoints,Tolerance,deltaT,RewardGain)
            if nargin>0
                NewDomain.Bounds = Bounds;
                NewDomain.StartState = StartState;
                NewDomain.Waypoints = Waypoints;
                NewDomain.Tolerance = Tolerance;
                NewDomain.deltaT = deltaT;
                NewDomain.RewardGain = RewardGain;
                
            else
                %Default bounds values
                NewDomain.Bounds.Xmax = 5;
                NewDomain.Bounds.Xmin = -5;
                NewDomain.Bounds.Ymax = 5;
                NewDomain.Bounds.Ymin = -5;
                
                %Default forward speed
                NewDomain.Speed = 0.5;
                
                %Randomly generate the start state
                NewDomain.StartState.x = (NewDomain.Bounds.Xmax - NewDomain.Bounds.Xmin)*rand(1,1) + NewDomain.Bounds.Xmin;
                NewDomain.StartState.y = (NewDomain.Bounds.Ymax - NewDomain.Bounds.Ymin)*rand(1,1) + NewDomain.Bounds.Ymin;
                NewDomain.StartState.theta = 2*pi*rand(1,1) - pi;
                NewDomain.StartState.t = 0;
                
                %Generate an empty waypoint struct array
                NewDomain.Waypoints = struct('x',{},'y',{});
                
                %Default tolerance
                NewDomain.Tolerance = 0.2;
                
                %Default simulation time
                NewDomain.deltaT = 0.1;
                
                %Default Reward Gain
                NewDomain.RewardGain = 0.5;
                
            end
            
            NewDomain.CurrentState = NewDomain.StartState;
            TrajEntry = NewDomain.StartState;
            TrajEntry.reward = 0;
            TrajEntry.control = 0;
            NewDomain.Trajectory = struct2table(TrajEntry);
            
        end
        
        function SetWaypoints(NewDomain,Waypoints)
            NewDomain.Waypoints = Waypoints;
        end
        
        function SetStartState(NewDomain,StartState)
            NewDomain.StartState = StartState;
            NewDomain.StartState.t = 0;
            NewDomain.CurrentState = NewDomain.StartState;
            TrajEntry = NewDomain.StartState;
            TrajEntry.reward = 0;
            TrajEntry.control = 0;
            NewDomain.Trajectory = struct2table(TrajEntry);
        end
        
        function X = VectorizeState(NewDomain)
            X(1,1) = NewDomain.CurrentState.x;
            X(2,1) = NewDomain.CurrentState.y;
            X(3,1) = NewDomain.CurrentState.theta;
        end
        
        function XDot = StateDerivative(NewDomain,X,Control)
            XDot(1,1) = NewDomain.Speed*cos(X(3));
            XDot(2,1) = NewDomain.Speed*sin(X(3));
            XDot(3,1) = Control;            
        end
        
        function TrajEntry = PropogateState(NewDomain,Control)
            % PropogateState(NewDomain,Control)
            
            % Propogates the state forward by a constant time step with a
            % constant control input
            
            X = NewDomain.VectorizeState();
            [~,y] = ode45(@(t,x)NewDomain.StateDerivative(x,Control),[0 NewDomain.deltaT],X);
            FinalState = y(end,:);
            
            %Update the state of the Domain
            NewDomain.CurrentState.t = NewDomain.CurrentState.t + NewDomain.deltaT;
            NewDomain.CurrentState.x = FinalState(1);
            NewDomain.CurrentState.y = FinalState(2);
            NewDomain.CurrentState.theta = wrapToPi(FinalState(3));
            
            %Add the state to the trajectory
            TrajEntry =  NewDomain.CurrentState;
            TrajEntry.reward = -0.1 - NewDomain.RewardGain*Control^2;
            TrajEntry.control = Control;
            NewDomain.Trajectory = [NewDomain.Trajectory; struct2table(TrajEntry)];
        end
        
        function Control = HeadingControl(NewDomain,NextWaypoint)
            % Control = HeadingControl(NewDomain,NextWaypoint)
            % Computes the heading control based on proportional control
            %NextWaypoint is the index of the next waypoint
            
            %Implement a simple proportional control to head to the new
            %heading
            Kp = 3;
            CurrentHeading = NewDomain.CurrentState.theta;
            RequiredHeading = atan2((NewDomain.Waypoints(NextWaypoint).y - NewDomain.CurrentState.y),(NewDomain.Waypoints(NextWaypoint).x - NewDomain.CurrentState.x));
            
            Control = Kp*angdiff(CurrentHeading,RequiredHeading);
        end
        
        function PlotDomain(NewDomain)
            %Plot the waypoints
            nWaypoints = length(NewDomain.Waypoints);
            centers = zeros(nWaypoints,2);
            radii = zeros(nWaypoints,1);
            for iWaypoints = 1:nWaypoints
                centers (iWaypoints,:) = [NewDomain.Waypoints(iWaypoints).x NewDomain.Waypoints(iWaypoints).y];
                radii(iWaypoints,1) = NewDomain.Tolerance;
            end
            
            figure
            hold on
            axis equal
            xlim([NewDomain.Bounds.Xmin NewDomain.Bounds.Xmax]);
            ylim([NewDomain.Bounds.Ymin NewDomain.Bounds.Ymax]);
            viscircles(centers, radii);
            plot(centers(:,1),centers(:,2),'ro');
            size = min([(NewDomain.Bounds.Xmax - NewDomain.Bounds.Xmin) (NewDomain.Bounds.Ymax - NewDomain.Bounds.Ymin)])/100;
            
            %Plot the start state
            quiver(NewDomain.StartState.x, NewDomain.StartState.y, size*cos(NewDomain.StartState.theta), size*sin(NewDomain.StartState.theta),'Color','k');
            plot(NewDomain.StartState.x,NewDomain.StartState.y,'ko');
            
            %plot the trajectory so far
            plot(NewDomain.Trajectory.x(2:end), NewDomain.Trajectory.y(2:end),'bo');
            %quiver(NewDomain.Trajectory.x(2:end),NewDomain.Trajectory.y(2:end),size*cos(NewDomain.Trajectory.theta(2:end)),size*sin(NewDomain.Trajectory.theta(2:end)),'Color','b')
            
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
                    if WaypointError < NewDomain.Tolerance
                        currentWaypoint = currentWaypoint+1;
                    end
                end
            end
        end
        
            
            
        
    end
end
    



