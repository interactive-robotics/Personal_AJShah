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
    
    MAPEstimates
    %MAPEstimates[].tStep
    %MAPEstimates[].model
    % It is an array of the maximum aposteriori estimates of the
    % probability of a changepoint at each time, and the previous time
    % point at which it would have had a changepoint
    
    Parameters
    %Parameters.skillLength
    %Parameters.maxParticles
    %Parameters.minParticles
    end
    
    
    methods
        function NewCPD = CPD_PF(Models,ModelPriors,Parameters)
            
            NewCPD.ModelPriors = ModelPriors;
            nModels = length(Models);
            for i = 1:nModels
                Models(i).ModelPrior = ModelPriors(i);
            end
            NewCPD.Models = Models;
            NewCPD.Parameters = Parameters;
            NewCPD.Particles = Particle.empty();
            NewCPD.iCurrent = 0;
            NewCPD.tHist = [];
            NewCPD.MAPEstimates = struct('model',{[]},'tstep',{[]});
        end
        
        function ReceiveTrajectory(NewCPD,TrajEntry)
            
            %Update the CPD time
            NewCPD.iCurrent = NewCPD.iCurrent+1;
            NewCPD.tHist = [NewCPD.tHist TrajEntry.t];
            
            %First update the model statistics and trajectory entries
            nParticles = length(NewCPD.Particles);
            if ~isempty(NewCPD.Particles)                
                for i = 1:nParticles
                    NewCPD.Particles(i).ReceiveTrajectory(TrajEntry,NewCPD.Parameters.skillLength);
                end
            end
            
            
            %If the number of particles equals maximum particle count,
            %resample down to requisite max particles
            if nParticles >= NewCPD.Parameters.maxParticles
                % Use the stratified optimal resampling algorithm to
                % resample the particles
                NewCPD.ResampleParticles
            end
            
            %Obtain the most likely particle for the previous changepoint
            %and append the most likely path
            if ~isempty(NewCPD.Particles)
            [maxMAP, particleIndex] = max([NewCPD.Particles(:).MAP]);
            NewMAPEstimates.tstep = NewCPD.Particles(particleIndex).tBegin;
            NewMAPEstimates.model = NewCPD.Particles(particleIndex).Model;
            NewCPD.MAPEstimates = [NewCPD.MAPEstimates; NewMAPEstimates];
            else
                nModels = length(NewCPD.Models);
                maxMAP = 1/nModels;
            end
            
            %Generate New particles for the current time step for each of
            %the models
            
            for iModel = 1:length(NewCPD.Models)
                NewParticle = Particle(NewCPD.iCurrent,NewCPD.Models(iModel),maxMAP,NewCPD.MAPEstimates);
                NewCPD.Particles = [NewCPD.Particles NewParticle];
            end
            
            
        end
        
        function ResampleParticles(NewCPD)
            % Use the stratified optimal resampling algorithm to sample
            % down the number of particles
            
            % Compute the cut-off weight
            weights = [NewCPD.Particles(:).Ptjq]/sum([NewCPD.Particles(:).Ptjq]);
            alpha = calculate_alpha(weights,NewCPD.Parameters.minParticles);
            
            nParticles = length(NewCPD.Particles);
            u = alpha*rand();
            resample = zeros(nParticles,1);
            
            for iParticle = 1:nParticles
                if weights(iParticle) >= alpha
                    resample(iParticle) = 1;
                else 
                    u = u - weights(iParticle);
                    if u <= 0
                        resample(iParticle) = 1;
                        u=u+alpha;
                    end
                end                        
            end
            
            indices = find(resample);
            ResampledParticles = NewCPD.Particles(indices);
            NewCPD.Particles = ResampledParticles;
        end
        
        
        function Changepoints = LookBack(NewCPD)
            tCurr = NewCPD.iCurrent-1;
            prevChangepoint = NewCPD.MAPEstimates(tCurr).tstep;
            prevModel = NewCPD.MAPEstimates(tCurr).model;
            Changepoints(1,1).tStep = prevChangepoint;
            Changepoints(1,1).model = prevModel;
            %tLookBack = tCurr;
            
            while prevChangepoint > 1
                prevModel = NewCPD.MAPEstimates(prevChangepoint).model;
                prevChangepoint = NewCPD.MAPEstimates(prevChangepoint).tstep;
                newChangepoint.tStep = prevChangepoint;
                newChangepoint.model = prevModel;
                Changepoints = [Changepoints; newChangepoint];
            end
        end
    end
end