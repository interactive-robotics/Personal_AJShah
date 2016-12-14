function [lkh, w] = fit_model_fearn(x, y, int, bfs)

params = get_parameters();

v = params.prior_v;
gam = params.prior_gamma;
delta = params.prior_delta;

n = size(int, 2);

phi = bfs(x(1));
nphi = size(phi, 2);

H = zeros(nphi, n);
D = eye(nphi, nphi)*delta;
pos = 1;

for j = int
    H(:, pos) = bfs(x(j));
    pos = pos + 1;
end;

M = inv(H*H' + inv(D));
P = (eye(n, n) - H'*M*H);

yy = y(int);
yP2 = yy*P*yy';

term1 = ((yP2 + gam)^((n + v)/2));
term1 = term1 / sqrt(det(M)/det(D));
term1 = term1 / gam^(v/2);
term1 = term1 / gamma((n + v) / 2);
term1 = term1 * gamma(v/2);

lkh = pi^(-(n)/2)/term1;

lt = -(n/2)*log(pi);
lt = lt + 0.5*log(det(M)/det(D));
lt = lt + (v/2)*log(gam);
lt = lt - (n+v/2)*log(yP2 + gam);
lt = lt + gammaln((n+v)/2);
lt = lt - gammaln((v/2));

lkh = lt;
w = 0;

%w = pinv(A + eye()*alpha)' * b;
%outy = (A'*w)';

%plot(x, y, 'r+'); hold on;
%plot(x(int), outy, 'b'); 

%err = sum((y(int) - outy).^2);
%beta = n / err;

%ll = (-(beta/2) * err) + ((n/2)*log(beta)) - ((n/2)*log(2*pi));

% This normalizes it so that the maximum value is 1.
% ll - (n/2)*log(beta) + (n/2)*log(2*pi)

% Equivalently
% ll = -n/2 + ((n/2)*(log(n) - log(err))) - ((n/2)*log(2*pi))

%(-(beta/2) * err)
%((n/2)*log(beta)) 
%-((n/2)*log(2*pi))


%bic = ll - 0.5*nphi*log(n);

