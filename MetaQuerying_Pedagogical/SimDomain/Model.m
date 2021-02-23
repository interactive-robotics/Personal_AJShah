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
        
    end
    
    methods
        
        function NewModel = Model(Params, Basis)
            NewModel.Parameters = Params;
            NewModel.Basis = Basis;
            NewModel.ModelPrior = 1;
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