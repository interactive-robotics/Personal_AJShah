function G = GeometricPDF(interval)

%G = 0;

% Sum over pmfs for each.
%for j = 1:interval
%    G = G + GeometricPMF(j);
%end;

params = get_parameters();
p = params.prior_lambda;
G = (1 - (1-p)^interval);
