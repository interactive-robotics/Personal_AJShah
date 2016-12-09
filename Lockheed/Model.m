classdef Model < handle
    
    properties
        Basis
        %Basis.order
        %Basis.Bounds
        %Basis.dimension
        %Basis.Size
        
        Params
        %Params.delta
        %Params.sigma2v
        %Params.betav
        %Params.skillLength
        %Params.discount
        
        Statistics
        %Statistics.Aq
        %Statistics.zq
        %Statistics.bq;
        %Statistics.tr_1q
        %Statistics.sum_rq
        %Statistics.tr_2q
        %The initial stats values depend on the Basis parameters and the
        
        ModelEvidence
        %A function of time
        
        Ptjq
        % Ptjq[]
        %Probability of previous changepoint occuring at t
        
        tCurrent
        
        t
        
    end
    
    methods
        
        function NewModel = Model(Params, Basis)
            NewModel.Params = Params;
            NewModel.Basis = Basis;
            BasisSize = (NewModel.Basis.order+1)^NewModel.Basis.dimension;
            NewModel.Statistics.Aq = zeros(BasisSize,BasisSize);
            NewModel.Statistics.zq = zeros(BasisSize,1);
            NewModel.Statistics.bq = zeros(BasisSize,1);
            NewModel.Statistics.tr_1q = 0;
            NewModel.Statistics.sum_rq = 0;
            NewModel.Statistics.tr_2q = 0;
            
            NewModel.tCurrent = 1;
            
            NewModel.ModelEvidence = struct('Pjt',{},'C1',{},'C2',{},'C3',{},'C4',{},'yq',{});
            
            NewModel.Ptjq = [];
            
            NewModel.t = 0;
        end
        
        function [Pjt, C1, C2, C3, C4, yq] = ComputeModelEvidence(NewModel,t,j)
            Aq = NewModel.Statistics(j).Aq;
            %zq = NewModel.Statistics(j).zq;
            bq = NewModel.Statistics(j).bq;
            %tr_1q = NewModel.Statistics(j).tr_1q;
            %tr_2q = NewModel.Statistics(j).tr_2q;
            sum_rq = NewModel.Statistics(j).sum_rq;
            delta = NewModel.Params.delta;
            %sigma2v = NewModel.Params.sigma2v;
            %betav = NewModel.Params.betav;
            u = NewModel.Params.u;
            v = NewModel.Params.v;
            BasisSize = (NewModel.Basis.order+1)^NewModel.Basis.dimension;
            
            D = (1/delta)*eye(BasisSize);
            invAqD = inv(Aq+D);
            yq = sum_rq - bq'*invAqD*bq;
            %u = sigma2v + betav; 
            %v = betav/sigma2v - 1;
            m = BasisSize;
            n = t-j;
            
            Pjt = (pi^(-n/2)/sqrt(delta^m))*sqrt(det(invAqD))*(u^(v/2)/(yq + u)^((n+v)/2))*(gamma((n+v)/2)/gamma(v/2));
            %Pjt = (pi^(-n/2)/(delta^m))*sqrt(det(invAqD))*(u^(v/2)/(yq + u)^((n+v)/2))*(gamma((n+v)/2)/gamma(v/2));
            C1 = (pi^(-n/2)/delta^m);
            C2 = sqrt(det(invAqD));
            C3 = (u^(v/2)/(yq + u)^((n+v)/2));
            C4 = (gamma((n+v)/2)/gamma(v/2));            
        end
        
        function UpdateModelStatistics(NewModel,TrajEntry)
            %Debug/Check once again
            discount = NewModel.Params.discount;
            tIndexMax = NewModel.tCurrent-1;
            %Initialize the statistics for the last time instant
            BasisSize = (NewModel.Basis.order+1)^NewModel.Basis.dimension;
            NewModel.Statistics(tIndexMax,1).Aq = zeros(BasisSize,BasisSize);
            NewModel.Statistics(tIndexMax,1).zq = zeros(BasisSize,1);
            NewModel.Statistics(tIndexMax,1).bq = zeros(BasisSize,1);
            NewModel.Statistics(tIndexMax,1).tr_1q = 0;
            NewModel.Statistics(tIndexMax,1).sum_rq = 0;
            NewModel.Statistics(tIndexMax,1).tr_2q = 0;
            
            for tIndex = 1:(NewModel.tCurrent-1)
                
                Aq = NewModel.Statistics(tIndex,1).Aq;
                zq = NewModel.Statistics(tIndex,1).zq;
                bq = NewModel.Statistics(tIndex,1).bq;
                tr_1q = NewModel.Statistics(tIndex,1).tr_1q;
                tr_2q = NewModel.Statistics(tIndex,1).tr_2q;
                sum_rq = NewModel.Statistics(tIndex,1).sum_rq;
                
                PhiX = NewModel.ComputeBasis(TrajEntry);
                NewModel.Statistics(tIndex,1).Aq = Aq + PhiX*PhiX';
                NewModel.Statistics(tIndex,1).zq = discount*zq + PhiX;
                NewModel.Statistics(tIndex,1).bq = bq + TrajEntry.reward*zq;
                NewModel.Statistics(tIndex,1).tr_1q = 1 + (discount^2)*tr_1q;
                NewModel.Statistics(tIndex,1).sum_rq = sum_rq + (TrajEntry.reward^2)*tr_1q + 2*discount*TrajEntry.reward*tr_2q;
                NewModel.Statistics(tIndex,1).tr_2q = discount*tr_2q + TrajEntry.reward*tr_1q;
            end
        end
        
        function output = ComputeBasis(NewModel,TrajEntry)
            %Scale the trajectory state vector by the bounds
            scaledX = zeros(size(TrajEntry.X));
            for iDim = 1:NewModel.Basis.dimension
                scaledX(iDim) = (TrajEntry.X(iDim) - NewModel.Basis.Bounds(iDim).min)/(NewModel.Basis.Bounds(iDim).max - NewModel.Basis.Bounds(iDim).min)*2 - 1;
            end
            output = FourierBasis(scaledX,NewModel.Basis.order);
        end
        
        function UpdateModelEvidence(NewModel)
            nSize = size(NewModel.Statistics,1);
            for tStep = 1:nSize
                [ME.Pjt, ME.C1, ME.C2, ME.C3, ME.C4, ME.yq] = NewModel.ComputeModelEvidence(NewModel.tCurrent,tStep); 
                NewModel.ModelEvidence(tStep) = ME;
            end
        end
        
        function UpdatePtjq(NewModel,MAPEstimates, ModelPrior, skillLength)
            p = 1/skillLength;
            for itStep = 1:NewModel.tCurrent-1
                C1 = 1 - geocdf(NewModel.tCurrent - itStep - 1,p);
                C2 = NewModel.ModelEvidence(itStep).Pjt;
                C3 = ModelPrior;
                C4 = MAPEstimates(itStep).P;
                NewModel.Ptjq(itStep,1) = C1*C2*C3*C4;
            end
        end
        
        function ReceiveNewTrajEntry(NewModel,TrajEntry,MAPEstimates,ModelPrior,skillLength)
            NewModel.tCurrent = NewModel.tCurrent+1;
            NewModel.t = [NewModel.t; TrajEntry.t];
            NewModel.UpdateModelStatistics(TrajEntry);
            %Update the model evidence
            NewModel.UpdateModelEvidence();
            if nargin>2 %if called only with 2 arguments, then being called from the test script
            NewModel.UpdatePtjq(MAPEstimates,ModelPrior,skillLength);
            end
            
            
        end
        
        
        
    end    
end