nTraj = 50;
Trajs = cell(0,1);

for i = 1:nTraj    
    dataFilename = sprintf('Predicates_%i.json',i);
    filename = strcat('CustomDomain100','/',dataFilename);
    text = fileread(char(filename));
    Trajectory = jsondecode(text);
    Trajs{i} = Trajectory;
    clear Trajectory;    
end

fid = fopen('texada_log.txt','w')

for i = 1:length(Trajs)
    Trajectory = Trajs{i};
    for j = 1:size(Trajectory.WaypointPredicates,2)
        %Write all the waypoint predicates
        
        for k = 1:size(Trajectory.WaypointPredicates,1)
            if Trajectory.WaypointPredicates(k,j)== 0
                fprintf(fid,'False');
            else
                fprintf(fid,'True');
            end
        end
        
        for k = 1:size(Trajectory.PositionPredicates,1)
            if Trajectory.PositionPredicates(k,j)== 0
                fprintf(fid,'False');
            else
                fprintf(fid,'True');
            end
        end
        
        for k = 1:size(Trajectory.ThreatPredicates,1)
            if Trajectory.ThreatPredicates(k,j)== 0
                fprintf(fid,'False');
            else
                fprintf(fid,'True');
            end
        end 
        
        fprintf(fid,'\n');
    end
    fprintf(fid,'--\n');
end
