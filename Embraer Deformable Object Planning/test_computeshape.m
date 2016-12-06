% Test script for the cable shape computation
Length = 10;
stiffness = 0.01;

x_initial = 0;
y_initial = 0.3;
theta_initial = 0;

X_init = [x_initial;y_initial;theta_initial];

x_final = 0.2;
y_final = 0.6;
theta_final = 0;

X_final = [x_final; y_final; theta_final];

sol = ComputeShape2BVP(X_init, X_final, Length, stiffness);
plot(sol.y(1,:) , sol.y(2,:))
axis equal

sol = ComputeShapeBVPfree(X_init, 2   , 0.01 , 'left');
plot(sol.y(1,:), sol.y(2,:))
axis equal

figure(2)
plot(sol.x , sol.y(1:2,:))