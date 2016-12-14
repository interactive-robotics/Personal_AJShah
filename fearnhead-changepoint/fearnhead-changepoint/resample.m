function [cc ww] = resample(c, w, M)

a = calculate_alpha(w, M);

pos = 1;

for j = 1:size(w, 2)

    if(w(j) >= a)
        
        ww(pos) = w(j);
        cc(pos) = c(j);
        
        pos = pos + 1;
        
    end;
    
end;

A = M - (pos - 1);

% Remove sampled particles. 
smaller = (w < a); 

aa = a;

wv = w(find(smaller == 1));
c = c(find(smaller == 1));

% Normalize
div = sum(wv);
wv = wv / div;

% We now need to resample A more particles.

% Compute new alpha.
a = calculate_alpha(wv, A);

% Realize uniformly distributed random variable in [0, a].
u = rand()*a;
i = 1;

while i <= size(wv, 2)
    
    if(wv(i) >= a)
        
        ww(pos) = wv(i)*div;
        cc(pos) = c(i);
        
        pos = pos + 1;
        
    else
        
        u = u - wv(i);
        
        if u <= 0
            
            ww(pos) = a*div;
            cc(pos) = c(i);
            
            pos = pos + 1;
            
            u = u + a;
        end;
        
    end;
    
    i = i + 1;
    
end;
