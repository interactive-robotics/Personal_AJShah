w = rand(50,1);

alphaVal = linspace(0,1,100);

sum = zeros(length(alphaVal),1);
for j = 1:length(alphaVal)
    
    for i=1:size(w,1)
        sum(j) = sum(j) + min([1,w(i)/alphaVal(j)]);
    end
end

plot(alphaVal,sum)