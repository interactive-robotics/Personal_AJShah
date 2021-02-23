function [ Basis, ScaledX ] = ComputeBasis( Traj , Bounds, order )
% Computes the fourier basis of the specified order

ScaledX(1,1) = (Traj.x - Bounds.Xmin)/(Bounds.Xmax - Bounds.Xmin)*2 - 1;
ScaledX(2,1) = (Traj.y - Bounds.Ymin)/(Bounds.Ymax - Bounds.Ymin)*2 - 1;
ScaledX(3,1) = (Traj.theta + pi)/(2*pi)*2 - 1;

Basis = FourierBasis(ScaledX, order);
end

