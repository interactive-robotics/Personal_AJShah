clear all
%Define the model to be used for particles


%Define Basis information
Basis.order = 2;
Bounds(1).max = 5;
Bounds(1).min = -5;
Bounds(2).max = 5;
Bounds(2).min = -5;
Bounds(3).max = pi;
Bounds(3).min = -pi;
Basis.Bounds = Bounds;
Basis.dimension = 3;
Basis.size = (Basis.order+1)^Basis.dimension;

%Define Parameters
 
 Params.delta = 0.0001;
 %Params.sigma2v = 1;
 %Params.betav = 0.01;
 Params.u = 10;
 Params.v = 0.5;
 Params.SkillLength = 100;
 Params.discount = 0.9;
 
 NewModel = Model(Params,Basis);

%Load trajectory
load ExampleTraj3.mat

%Create the empty particles bank
Particles = Particle.empty();


%Create 1 new particle per time step, and update the statistics of all
%particles

for i = 1:10
    TrajEntryTable = (NewDomain.Trajectory(i,:));
    TrajEntry.t = TrajEntryTable.t;
    TrajEntry.X = [TrajEntryTable.x;TrajEntryTable.y;TrajEntryTable.theta];
    TrajEntry.reward = TrajEntryTable.reward;
    TrajEntry.U = TrajEntryTable.control;
    
    if ~isempty(Particles)
        nParticles = length(Particles);
        for j = 1:nParticles
            Particles(j).ReceiveTrajectory(TrajEntry,100)
        end
    end
    
    %Create a new particle for this time step
    NewParticle = Particle(i,NewModel,1,struct('model',{},'tStep',{}));
    Particles = [Particles; NewParticle];
    
end

weights = [Particles(:).Ptjq]/sum([Particles(:).Ptjq]);
minParticles = 5;
alpha = calculate_alpha(weights,minParticles);

nParticles = length(Particles);
u = alpha*rand();
resample = zeros(nParticles,1);
for i=1:nParticles
    if weights(i)>= alpha
        resample(i) = 1;
    else
        u = u-weights(i);
        if u<=0
            resample(i) = 1;
            u=u+alpha;
        end
    end
end

indices = find(resample);
NewParticles = Particles(indices);