clear all

% Define the input parameters for the cable
Length = 1.01;
stiffness = 0.5;
x_initial = 0;
y_initial = 0;
theta_initial = 0;

x_final = 1.0;
y_final = 0;
theta_final = 0;

% Transform into the baseline configuration of unit length

%First translate
x1_initial = 0;
y1_initial = 0;

x1_final = x_final - x_initial;
y1_final = y_final - y_initial;

% Next scale the cable lengths
xSolve_initial = x1_initial/Length;
ySolve_initial = y1_initial/Length;

xSolve_final = x1_final/Length;
ySolve_final = y1_final/Length;

% Solve for the cable configuration in the normalised coordinates
tGuess = linspace(0,1,150);
i=1;

% for stiffness = [ 0.01 0.1 0.5];
% Generate guess and boundary condition vectors
Xa_ref = [xSolve_initial;ySolve_initial;theta_initial];
Xb_ref = [xSolve_final;ySolve_final;theta_final];

Xa_guess = [xSolve_initial;ySolve_initial;-1;1;-5;2];
Xb_guess = [xSolve_final;ySolve_final;1;1;0;0];

%Generate function handles
bvpbcfun = @(Xa,Xb)CableDynamics2Dbcfun(Xa,Xb,Xa_ref,Xb_ref);
guessfun = @(t)CableDynamics2Dguess(t,Xa_guess,Xb_guess);
odefun = @(t,X)CableDynamics2Dodefun(t,X,stiffness);


solinit = bvpinit(tGuess,guessfun);
% load guess
%  solinit = sol;
%  solinit.x = (solinit.x)*3;
%  solinit.y = (solinit.y)*3
%  clear sol

sol = bvp4c(odefun, bvpbcfun, solinit);

coordSolve(i).X(1,:) = sol.y(1,:);
coordSolve(i).Y(1,:) = sol.y(2,:);
i=i+1;
%save guess.mat sol;

%end

% Transform back to the original coordinate frame
% Scale to the original length
coord1.X = coordSolve.X*Length;
coord1.Y = coordSolve.Y*Length;

%Translate to original position
coord.X = coord1.X + x_initial;
coord.Y = coord1.Y + y_initial



axis equal
%hold on

figure(1)

plot(coord(1).X,coord(1).Y)
grid on
axis equal
% figure(2)
% plot(sol.x , sol.y)

