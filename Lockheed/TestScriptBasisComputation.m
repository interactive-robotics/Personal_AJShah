load ExampleTraj.mat

TrajLength = size(NewDomain.Trajectory,1);
for i=1:TrajLength
    TrajSample = NewDomain.Trajectory(i,:);
    [Basis ScaledX] = ComputeBasis(TrajSample,NewDomain.Bounds,3);
    ScaledFeatures(i,:) = ScaledX';
end