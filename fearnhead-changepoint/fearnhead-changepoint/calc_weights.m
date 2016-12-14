function wt = calc_weights(x, y, j, k)

% Number of models
q = 1;

top =  zeros(q, 1);
bottom = zeros(q, 1);
mx = 0;

for qval = 1:q
            
    fhandle = @line_bfs;
            
    if qval == 2
       fhandle = @line_bfs2;
    end;
              
    [top(qval), w] = fit_model_fearn(x, y, j+1:k, fhandle);
                        
    if j ~= k-1       
      [bottom(qval), w] = fit_model_fearn(x, y, j+1:k-1, fhandle);
      mx = max(top(qval), max(bottom(qval), mx));
    end;
          
end;
        
stop = 0;
sbottom = 0;
        
for qval = 1:q  
    stop = stop + exp(top(qval) - mx)*(1/q);
    sbottom = sbottom + exp(bottom(qval) - mx)*(1/q);           
end; 

wt = stop / sbottom;