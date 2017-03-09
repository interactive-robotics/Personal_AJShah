classdef Model < handle
    
    % This is the particle filter implementation for the class model. This
    % is distinct from the exact inferencec class model.
    
    properties
        Basis
        %Basis.order
        %Basis.Bounds
        %Basis.dimension
        %Basis.Size
        
        Parameters
        %Params.delta
        %Params.sigma2v
        %Params.betav
        %Params.skillLength
        %Params.discount
        
        ModelPrior
        
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
            NewModel.ModelPrior = 1;
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
        

        
        function output = ComputeBasis(NewModel,TrajEntry) %Keep
            %Scale the trajectory state vector by the bounds
            scaledX = zeros(size(TrajEntry.X));
            for iDim = 1:NewModel.Basis.dimension
                scaledX(iDim) = (TrajEntry.X(iDim) - NewModel.Basis.Bounds(iDim).min)/(NewModel.Basis.Bounds(iDim).max - NewModel.Basis.Bounds(iDim).min)*2 - 1;
            end
            output = FourierBasis(scaledX,NewModel.Basis.order);
        end        
        
    end    
end