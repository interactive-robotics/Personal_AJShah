y = gen_data(100);
x = [1:100];

subplot(4, 1, 1);
plot(x,  y, 'r+');

sz = size(x, 2);

% PrC(a, b + 1) = Pr(Ct = b | y1:a)

params = get_parameters();
max_particles = params.max_particles;
min_particles = params.min_particles;

w = zeros(max_particles, 1);
PrC = zeros(max_particles, max_particles);
num_particles = zeros(max_particles, 1);
index = zeros(max_particles, max_particles);

% Initialize
PrC(1, 1) = 1;
num_particles(1) = 1;
index(1, 1) = 0;


% Loop through the data
for k = 2:sz
    
    % for each incoming data point ...
    
    % Compute weights.
    for j = 0:num_particles(k-1)-1
        w(j+1) = calc_weights(x, y, index(k-1, j+1), k);
    end;  
    
    w(num_particles(k-1) + 1) = calc_weights(x, y, k-1, k);   
  
   % Update each conditional probability.
    for j = 0:num_particles(k-1)
       
       jj = index(k-1, j+1); 
        
       if j < num_particles(k-1)
           
           gfac = ((1 - GeometricPDF(k-1-jj))/(1 - GeometricPDF(k-1-jj-1)));
           PrC(k,j+1) = w(j+1) * gfac * PrC(k-1,j+1);
       
           index(k, j+1) = index(k-1, j+1);
           
       else
           
           sm = 0;
           
           for z = 0:num_particles(k-1)-1
               
               zz = index(k-1, z+1);
               
               gfac = (GeometricPDF(k-1-zz) - GeometricPDF(k-1-zz-1))/(1 - GeometricPDF(k-1-zz-1)); 
               sm = sm + gfac*PrC(k-1, z+1);
           end;
           
           PrC(k, j+1) = w(j+1) * sm;
           
           index(k, j+1) = k-1;
           
       end;
         
    end;

    % Need to renormalize these.
    st = sum(PrC(k, :));
    PrC(k, :) = PrC(k, :) / st;
    
    num_particles(k) = num_particles(k-1) + 1;
    
    % Check for resample
    if(num_particles(k) == max_particles)
        
        np = max_particles;
        
        [ind pp] = resample(index(k, 1:np), PrC(k, 1:np), min_particles);
        PrC(k, 1:min_particles) = pp;
        index(k, 1:min_particles) = ind;
        
        num_particles(k) = min_particles;
   
    end;
    
    % Plotting
    subplot(4, 1, 1);
    plot(x(1:k), y(1:k), 'r+');
    axis([1 sz min(y) max(y)]);
    ylabel('data');
    
    subplot(4, 1, 2);
    plot(index(k, 1:num_particles(k)), w(1:num_particles(k)), 'go');
    axis([0 sz 0 0.02]);
    ylabel('weights');
    
    subplot(4, 1, 3);
    plot(index(k, 1:num_particles(k)), PrC(k, 1:num_particles(k)), 'bo');
    ylabel('changepoint probs');
    axis([0 sz 0 1]);
    
    subplot(4, 1, 4);
    plot(1:k, num_particles(1:k), 'k');
    ylabel('particles');
    axis([1 sz 1 max_particles]);
     
    pause(0.01);
end;

% Find MAP solution.
pos = sz;

subplot(4, 1, 1);
hold on;  

while pos > 0
    
    [val ps] = max(PrC(pos, :));
    
    pos = index(pos, ps);
    
    plot([pos-1 pos-1], [min(y) max(y)], 'k--');
    
end;
