classdef Particle < handle
    
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
        
        ModelEvidence
        
        Ptjq
        % The weight of the particle in the posterior changepoint
        % distribution
        
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
        function NewParticle = Particle(tBegin, Model, prev_MAP, MAPEstimates)
            
            NewParticle.tBegin = tBegin;
            NewParticle.Model = Model;
            NewParticle.prev_MAP = prev_MAP;
            NewParticle.tCurrent = tBegin;
            NewParticle.MAP = 0;
            NewParticle.Ptjq = 0;
            NewParticle.ModelEvidence = 0;
            
            %Initialize the sufficient statistics to compute fit
            %probability
            BasisSize = (NewParticle.Model.Basis.order+1)^NewParticle.Model.Basis.dimension;
            NewParticle.Statistics(1,1).Aq = zeros(BasisSize,BasisSize);
            NewParticle.Statistics(1,1).zq = zeros(BasisSize,1);
            NewParticle.Statistics(1,1).bq = zeros(BasisSize,1);
            NewParticle.Statistics(1,1).tr_1q = 0;
            NewParticle.Statistics(1,1).sum_rq = 0;
            NewParticle.Statistics(1,1).tr_2q = 0;
            
            %Initialize the path estimates
            NewParticle.MAPEstimates = MAPEstimates;
            
            
        end
        
        function ReceiveTrajectory(NewParticle,TrajEntry,skillLength)
            NewParticle.tCurrent = NewParticle.tCurrent+1;
            NewParticle.UpdateStatistics(TrajEntry);
            NewParticle.ComputeModelEvidence();
            NewParticle.ComputePtjq(skillLength);
            NewParticle.ComputeMAP(skillLength);
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
        
        function ComputeModelEvidence(NewParticle)
            Aq = NewParticle.Statistics.Aq;
            bq = NewParticle.Statistics.bq;
            sum_rq = NewParticle.Statistics.sum_rq;
            delta = NewParticle.Model.Parameters.delta;
            u = NewParticle.Model.Parameters.u;
            v = NewParticle.Model.Parameters.v;
            BasisSize = (NewParticle.Model.Basis.order+1)^NewParticle.Model.Basis.dimension;
            
            D = (1/delta)*eye(BasisSize);
            invAqD = inv(Aq+D);
            yq = sum_rq-bq'*invAqD*bq;
            m = BasisSize;
            n = NewParticle.tCurrent-NewParticle.tBegin;
            
            C1 = (pi^(-n/2)/delta^m);
            C2 = sqrt(det(invAqD));
            C3 = (u^(v/2)/(yq + u)^((n+v)/2));
            C4 = (gamma((n+v)/2)/gamma(v/2));
            NewParticle.ModelEvidence = C1*C2*C3*C4;
            
        end
        
        function ComputePtjq(NewParticle,skillLength)
            p = 1/skillLength;
            C1 = 1 - geocdf((NewParticle.tCurrent - NewParticle.tBegin - 1) , p);
            C2 = NewParticle.ModelEvidence;
            C3 = NewParticle.Model.ModelPrior;
            C4 = NewParticle.prev_MAP;
            NewParticle.Ptjq = C1*C2*C3*C4;
            
        end
        
        function ComputeMAP(NewParticle,  skillLength)
            p = 1/skillLength;
            NewParticle.MAP = (NewParticle.Ptjq*geopdf(NewParticle.tCurrent - NewParticle.tBegin,p))/(1-geocdf(NewParticle.tCurrent-NewParticle.tBegin-1,p));
        end
    end
end