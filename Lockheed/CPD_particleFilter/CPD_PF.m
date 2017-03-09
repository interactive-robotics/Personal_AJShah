classdef CPD_PF < handle
    
    properties
    Models
    %Models[]: An array of objects of the type Model
    
    ModelPriors
    % ModelPriors[]: An array containing the scalar probabilities for each
    % model
    
    Particles
    %Particles[]: An array of objects of type particles
    
    iCurrent
    % The index of the current time
    
    tHist
    % tHist[]: An array of scalars indicating time stamps
    
    MapEstimates
    %MAPEstimates[].P
    %MAPEstimates[].i
    % It is an array of the maximum aposteriori estimates of the
    % probability of a changepoint at each time, and the previous time
    % point at which it would have had a changepoint
    
    Parameters
    %Parameters.skillLength
    %Parameters.maxParticles
    end
    
    
    methods
        function NewCPD = CPD_PF(Models,ModelPriors,Parameters)
        end
        
        function ReceiveTrajectory(NewCPD,TrajEntry)
        end
        
    end
end