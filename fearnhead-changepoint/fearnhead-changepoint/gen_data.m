function y = gen_data(t)

b1 = floor(t/3);
b2 = floor(2*t/3);

%b1 = floor(rand() * t);
%b2 = floor(rand() * t);
%
%while(abs(b2 - b1) < 0.3*t)
%    b2 = floor(rand() * t);
%end;
%
%if(b1 > b2)
%    t1 = b2;
%    b2 = b1;
%    b1 = t1;
%end;

modelm = rand()*10 - 5;
modelc = rand()*20 - 1;
off = 0;

noise = 5;

%modelm
%plotmodelc

for i = 1:t
    
    y(i) = modelm*((i - off)*100/t) + modelc + randn()*noise;
    
    if((i == b1) | (i == b2))
    
        mm = rand()*10 - 5;
        
        while(abs(mm - modelm) < 5)
            mm = rand()*10 - 5;
        end;
        
        modelm = mm;        
        
        off = i;
        
        modelc = y(i);
    end;
end;

%figure(2);
%plot(y, 'bo');
%hold on;

%miny = min(y);
%maxy = max(y);

%plot([b1 b1], [miny maxy], 'k-');
%plot([b2 b2], [miny maxy], 'k-');



