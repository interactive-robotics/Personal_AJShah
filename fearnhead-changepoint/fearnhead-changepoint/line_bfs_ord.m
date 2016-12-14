function phi = line_bfs_ord(x, ord)

phi = zeros(1, ord + 1);

phi(1) = 1;

for z = 1:ord
    phi(z + 1) = x^z;
end;

