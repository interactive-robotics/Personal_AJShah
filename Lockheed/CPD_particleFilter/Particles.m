classdef Particles < handle
    
    % A class for objects of type particles, which will be used for the CPD
    % algorithm with particle filtering
    
    properties
        tBegin
        %tBegin: A scalar for the time from which the particle was
        %instantiated
        
        Model
        %Model: A handle to an object of class model which is the model,
        %the particle is assumed to be adhering to
        
        MAP
        %MAP: The current scalar estimate of the a posteriori probability of changepoint. 
        
        MAPEstimates
        %The most likely path for the current particle
        
        prev_MAP
        % prev_MAP: The previous most likely MAP
        
        Statistics
        %Statistics.Aq
        %Statistics.zq
        %Statistics.bq;
        %Statistics.tr_1q
        %Statistics.sum_rq
        %Statistics.tr_2q
        %The initial stats values depend on the Basis parameters and the
        
        tCurrent
        %Current time index
    end
    
    methods
        function NewParticle = Particle(tBegin, Model, prev_Map)
            
            NewParticle.tBegin = tBegin;
            NewParticle.Model = Model;
            NewParticle.prev_Map = prev_MAP;
            NewParticle.tCurrent = tBegin;
            NewParticle.MAP = 0;
            
            %Initialize the sufficient statistics to compute fit
            %probability
            BasisSize = (NewParticle.Model.Basis.order+1)^NewParticle.Model.Basis.dimension;
            NewParticle.Statistics(tIndexMax,1).Aq = zeros(BasisSize,BasisSize);
            NewParticle.Statistics(tIndexMax,1).zq = zeros(BasisSize,1);
            NewParticle.Statistics(tIndexMax,1).bq = zeros(BasisSize,1);
            NewParticle.Statistics(tIndexMax,1).tr_1q = 0;
            NewParticle.Statistics(tIndexMax,1).sum_rq = 0;
            NewParticle.Statistics(tIndexMax,1).tr_2q = 0;
            
            
        end
        
        function ReceiveTrajectory(NewParticle,TrajEntry,skillLength)
            NewParticle.tCurrent = NewParticle.tCurrent+1;
            NewParticle.UpdateStatistics(TrajEntry);
            ModelEvidence = NewParticle.ComputeModelEvidence();
            Ptjq = NewParticle.ComputePtjq(ModelEvidence, skillLength);
            NewParticle.ComputeMAP(Ptjq, skillLength);
        end
        
        function UpdateStatistics(NewParticle, TrajEntry)
            discount = NewParticle.Model.Parameters.discount;
            Aq = NewParticle.Statistics.Aq;
            zq = NewParticle.Statistics.zq;
            bq = NewParticle.Statistics.bq;
            tr_1q = NewParticle.Statistics.tr_1q;
            tr_2q = NewParticle.Statistics.tr_2q;
            sum_rq = NewParticle.Statistics.sum_rq;
            Model = NewParticle.Model;
            
            %Update the statistics
            PhiX = Model.ComputeBasis(TrajEntry);
            NewParticle.Statistics.Aq = Aq + PhiX*PhiX';
            NewParticle.Statistics.zq = discount*zq + PhiX;
            NewParticle.Statistics.bq = bq + TrajEntry.reward*zq;
            NewParticle.Statistics.tr_1q = 1 + (discount^2)*tr_1q;
            NewParticle.Statistics.sum_rq = sum_rq + (TrajEntry.reward^2)*tr_1q + 2*discount*TrajEntry.reward*tr_2q;
            NewParticle.Statistics.tr_2q = discount*tr_2q + TrajEntry.reward*tr_1q;            
        end
        
        function ModelEvidence = ComputeModelEvidence(NewParticle)
            Aq = NewParticle.Statistics.Aq;
            bq = NewParticle.Statistics.bq;
            sum_rq = NewParticle.Statistics.sum_rq;
            delta = NewParticle.Model.Params.delta;
            u = NewParticle.Model.Params.u;
            v = NewParticle.Model.Params.v;
            BasisSize = (NewParticle.Model.Basis.order+1)^NewParticle.Model.Basis.Dimension;
            
            D = (1/delta)*eye(BasisSize);
            invAqD = inv(Aq+D);
            yq = sum_rq-bq'*invAqD*bq;
            m = BasisSize;
            n = NewParticle.tCurrent-NewParticle.tBegin;
            
            C1 = (pi^(-n/2)/delta^m);
            C2 = sqrt(det(invAqD));
            C3 = (u^(v/2)/(yq + u)^((n+v)/2));
            C4 = (gamma((n+v)/2)/gamma(v/2));
            ModelEvidence = C1*C2*C3*C4;
            
        end
        
        function Ptjq =  ComputePtjq(NewParticle,ModelEvidence,skillLength)
            p = 1/skillLength;
            C1 = 1 - geocdf((NewParticle.tCurrent - NewParticle.tBegin - 1) , p);
            C2 = ModelEvidence;
            C3 = NewParticle.Model.ModelPrior;
            C4 = NewParticle.prev_MAP;
            Ptjq = C1*C2*C3*C4;
        end
        
        function ComputeMAP(NewParticle, Ptjq,  skillLength)
            p = q/skillLength;
            NewParticle.MAP = (Ptjq*geopdf(NewParticle.tCurrent - NewParticle.tBegin,p))/(1-geocdf(NewParticle.tCurrent-NewParticle.tBegin-1,p));
        end
    end
end