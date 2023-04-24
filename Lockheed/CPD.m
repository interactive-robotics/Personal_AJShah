 classdef CPD < handle
    
    properties
        Models
        %Models[]: An array of objects of the type Model
        
        ModelPriors
        %ModelPriors[]: An array containing scalar prior probabilities of
        %the models
        
        MAPEstimates
        %MAPEstimates[].P
        %MAPEstimates[].i
        % It is an array of the maximum aposteriori estimates of the
        % probability of a changepoint at each time, and the previous time
        % point at which it would have had a changepoint
        
        tCurrent
        
        Parameters
        %Parameters.skillLength
        
        end
    
    methods
        
        function NewCPD = CPD(Models,ModelPriors, Parameters)
            NewCPD.Models = Models;
            NewCPD.ModelPriors = ModelPriors;
            NewCPD.Parameters = Parameters;
            NewCPD.MAPEstimates(1,1).P = 1;
            NewCPD.MAPEstimates(1,1).model = 0;
            NewCPD.MAPEstimates(1,1).tStep = 0;
            NewCPD.tCurrent = 1;
        end   
        
        function UpdatePMAP(NewCPD)
            p = 1/NewCPD.Parameters.skillLength;
            tCurr=NewCPD.tCurrent;
            maxPMAP = -0.1;
           % Models = NewCPD.Model;
            for iModel = 1:size(NewCPD.Models,1)
                for Tstep = 1:tCurr-1
                    candidatePMAP = (NewCPD.Models(iModel).Ptjq(Tstep)*geopdf(tCurr-Tstep,p))/(1 - geocdf(tCurr-Tstep-1,p));
                    if candidatePMAP >= maxPMAP
                        maxPMAP = candidatePMAP;
                        maxModel = iModel;
                        maxtstep = Tstep;
                    end
                end
            end
            NewCPD.MAPEstimates(tCurr,1).P = maxPMAP;
            NewCPD.MAPEstimates(tCurr,1).model = maxModel;
            NewCPD.MAPEstimates(tCurr,1).tStep = maxtstep;
        end
        
        function ReceiveTrajectory(NewCPD,TrajEntry)
            for iModel = 1:size(NewCPD.Models,1)
                NewCPD.tCurrent = NewCPD.tCurrent+1;
                NewCPD.Models(iModel).ReceiveNewTrajEntry(TrajEntry,NewCPD.MAPEstimates,NewCPD.ModelPriors,NewCPD.Parameters.skillLength);
            end
            NewCPD.UpdatePMAP();
        end
        
        function Changepoints = LookBack(NewCPD)
            tCurr = NewCPD.tCurrent;
            prevChangepoint = NewCPD.MAPEstimates(tCurr).tStep;
            prevModel = NewCPD.MAPEstimates(tCurr).model;
            Changepoints(1,1).tStep = prevChangepoint;
            Changepoints(1,1).model = prevModel;
            %tLookBack = tCurr;
            
            while prevChangepoint > 1
                prevModel = NewCPD.MAPEstimates(prevChangepoint).model;
                prevChangepoint = NewCPD.MAPEstimates(prevChangepoint).tStep;
                newChangepoint.tStep = prevChangepoint;
                newChangepoint.model = prevModel;
                Changepoints = [Changepoints; newChangepoint];
            end
        end
                
    end
            
end
    
        
  