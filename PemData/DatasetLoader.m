load FullTrajAndTaskTimes.mat

StandardData = experiment_data{1,1};
nSubjects = length(StandardData);

for i=1:nSubjects
    FilteredData{i}{1} = 
