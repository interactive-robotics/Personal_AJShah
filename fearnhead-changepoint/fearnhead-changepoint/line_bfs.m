function phi = line_bfs(x)

if nargin == 0
    phi = 2;
else
    phi = line_bfs_ord(x, 1);
end;
