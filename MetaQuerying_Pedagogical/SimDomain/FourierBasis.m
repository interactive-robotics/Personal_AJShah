function [ output ] = FourierBasis(X,order)
%Ensure that X is a column vector. Also ensure that the values of x are
%scaled by the domain bounds

nvar = length(X);
%Create the integer lattice for the fourier basis

argout = ndgrid2(nvar,[0:order]);
lattice = [];
for i = 1:nvar
lattice = [lattice argout{i}(:)];
end


output = zeros(size(lattice,1),1);
for iBasis = 1:size(lattice,1)
    output(iBasis) = cos(pi*lattice(iBasis,:)*X);
end
end

