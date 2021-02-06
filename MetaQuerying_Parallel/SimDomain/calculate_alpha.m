function a = calculate_alpha(w, M)

mn = 1;
mnpos = 1;

% There are faster ways to do this. 
% This will do for now. 
for j = 1:size(w, 2)
    
    val = w(j);
    
    ss = 0;
    
    for k = 1:size(w, 2)
        ss = ss + min(w(k)/val, 1);
    end;
    
    if ss <= M
        
        if val < mn
        
            mn = val;
            mnpos = j;
            
        end;
            
    end;
    
end;

% This bit is correct. 
larger = (w > mn);
Ak = sum(larger);
Bk = w*(1 - larger)';

% Check
% Bk/mn + Ak - M
% (seems to hold)

% Compute a
a = Bk/(M - Ak);
