function prm = get_parameters()

% NOTE: run clear_parameters() when you change this file!
% This is because the parameters are stored in a global variable
% to avoid having to recompute them every time. (they are
% accessed frequently). 

global PRMS;

if(size(PRMS, 1) <= 1)

    %--- Prior on length of skill.
    expt_length = 33; % 100 for pball
    PRMS.prior_lambda = (1/ expt_length);

    %--- Fitting priors

    % Regularization prior.
    PRMS.prior_delta = 1/0.0001;

    %--- Inverse gamma priors.

    % Assign expected variance mean.
    mu = 25; 

    % Assign shape parameter. Closest to mean
    % means broadest shape. 
    b = mu + 0.000001;
    a = b/mu - 1;

    PRMS.prior_v = 2*a;
    PRMS.prior_gamma = 2*b;

    %--- Particle filter parameters.
    PRMS.min_particles = 15; 
    PRMS.max_particles = 30; 

    %--- Fourier Basis parameters.
    PRMS.nvars = 1; 

    % Bias stuff
    PRMS.bias_delta = (0.05)^2;

end;

prm = PRMS;