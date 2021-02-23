classdef ReducedModel < Model
    
    methods
        function NewModel = ReducedModel(Params,Basis)
            NewModel@Model(Params,Basis)
        end
        
        function output = ComputeBasis(NewModel,TrajEntry)
            
            %Compute features
            
            %Compute fourier basis as per the bounds and the order defined
        
    end
end