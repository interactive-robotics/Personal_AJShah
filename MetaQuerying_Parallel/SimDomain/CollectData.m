nTraj = 50;
Correct_Trajs = cell(0,1);
CorrLengths = zeros(nTraj,1);
for i = 1:nTraj    
    
    dataFilename = sprintf('Data_%i.mat',i);
    load(strcat('CustomDomain100','/',dataFilename),'Trajectory');
    Correct_Trajs{i} = Trajectory;
    CorrLengths(i) = height(Trajectory);
    clear Trajectory;    
end

nIncorrTraj = 50;
Incorrect_Trajs = cell(0,1);
IncorrLengths = zeros(nIncorrTraj,1);
for i=1:nIncorrTraj
    dataFilename = sprintf('Data_%i.mat',i);
    load(strcat('CustomDomainCounter100','/',dataFilename),'Trajectory')
    Incorrect_Trajs{i} = Trajectory;
    IncorrLengths(i) = height(Trajectory);
    clear Trajectory;
end

maxLength = max([CorrLengths' IncorrLengths']);
minLength = min([CorrLengths' IncorrLengths']);

P = zeros(nTraj+nIncorrTraj,2,maxLength);

for i = 1:nTraj
    
    Trajectory = Correct_Trajs{i};
    Data  = Trajectory{:,{'x','y'}}';
    nPad = maxLength - size(Data,2);
    Data = padarray(Data,[0 nPad],'replicate','post');
    for j = 1:size(Data,1)
    P(i,j,:) = Data(j,:);
    end
end

for i = nTraj+1: nTraj+nIncorrTraj
    Trajectory = Incorrect_Trajs{i-nTraj};
    Data = Trajectory{:,{'x','y'}}';
    nPad = maxLength - size(Data,2);
    Data = padarray(Data,[0 nPad],'replicate','post');
    for j = 1:size(Data,1)
    P(i,j,:) = Data(j,:);
    end
end
    
s = [ones(nTraj,1) ; -ones(nIncorrTraj,1)];
V = [1 2];
L_max = 10;
t = 1:maxLength;
trunc = 0;
Plimit(1,1) = -5;
Plimit(1,2) = 5;
Plimit(2,1) = -5;
Plimit(2,2) = 5;
delta = 2;
J_max = 90;
Ns(1) = 10;
Ns(2) = 10;

disp('Initializing classification phase');
[phi_e,val_e,mn_e] = findformula(V,L_max,P,s,t,[trunc,max(t)],Plimit,Ns,[],delta,J_max);
disp(['Classification complete.  Classifying formula is ','$',interpret(phi_e,val_e),'$']);