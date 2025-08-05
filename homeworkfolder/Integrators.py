import numpy as np

# Constants of the spring (can be added as function parameters)
k = 1.0 # Spring constant [N/m]
m = 1.0 # Mass [kg]
g_const = 9.81 # Grav constant on the surface of the Earth [m/sec^2]

# Function which computes the right hand side of the hamornic oscillator
# Inputs:
# - pos: position in [m]
# - vel: velocity in [m/sec]
# Outputs:
# - rhs_pos: right hand side of position -> \dot{x} = rhs_x( x , v , t )
# - rhs_vel: right hand side of velocity -> \dot{v} = rhs_v( x , v , t )
def rhs_oscillator( pos , vel ):

    rhs_pos = vel # RHS of position is just velocity for any Newton problem
    rhs_vel = - k*pos/m # RHS of velocity for spring is just force / mass (acceleration)

    return rhs_pos, rhs_vel


# Euler integrator function:
# Inputs:
# - x0: initial position [m]
# - v0: initial velocity [m/sec]
# - t_i: initial time [sec]
# - t_f: final time [sec]
# - Npoints: number of points [-]
# Outputs:
# - time[ Npoints ]: time array holding [ t1 , t2 , t3 ... tN ]
# - pos[ Npoints ]: position array holding [ x1 , x2 , ... xN ]
# - vel[ Npoints ]: velocity array holding [ v1 , v2 , ... vN ]
def Euler_Solver( x0 , v0 , t_i , t_f , Npoints ):

    # Compute time step 
    # |  |  |  | -> intervals are always 1 less than the points
    dt = ( t_f - t_i )/( Npoints - 1.0 ) 
    # Create the time array
    time = np.linspace( t_i , t_f , Npoints ) 
    # Initialize empty position and velocity arrays
    pos = np.zeros( Npoints )
    vel = np.zeros( Npoints )
    # Assign initial position and velocity
    pos[ 0 ] = x0 # First element of position array is whatever user gave as initial position
    vel[ 0 ] = v0 # First element of velocity array is whatever user gave as initial velocity

    # Main integration loop
    for i in range( 0 , Npoints - 1 ):

        rhs_pos, rhs_vel = rhs_oscillator( pos[ i ] , vel[ i ] )
        # This is how we did it without RHS function abstraction
        pos[ i + 1 ] = pos[ i ] + rhs_pos*dt
        vel[ i + 1 ] = vel[ i ] + rhs_vel*dt
        '''
        # Position 1 moment in the future is just my current position + whatever my current velocity is times the time step
        pos[ i + 1 ] = pos[ i ] + vel[ i ]*dt
        # Velocity 1 moment in the future is just my current velocity + whatever my current acceleration is times the time step
        vel[ i + 1 ] = vel[ i ] + ( - k/m * pos[ i ] )*dt
        '''
    return time, pos, vel


# Verlet integrator function:
# Inputs:
# - x0: initial position [m]
# - v0: initial velocity [m/sec]
# - t_i: initial time [sec]
# - t_f: final time [sec]
# - Npoints: number of points [-]
# Outputs:
# - time[ Npoints ]: time array holding [ t1 , t2 , t3 ... tN ]
# - pos[ Npoints ]: position array holding [ x1 , x2 , ... xN ]
# - vel[ Npoints ]: velocity array holding [ v1 , v2 , ... vN ]
def Verlet_Solver( x0 , v0 , t_i , t_f , Npoints ):

    # Compute time step 
    # |  |  |  | -> intervals are always 1 less than the points
    dt = ( t_f - t_i )/( Npoints - 1.0 ) 
    # Create the time array
    time = np.linspace( t_i , t_f , Npoints ) 
    # Initialize empty position and velocity arrays
    pos = np.zeros( Npoints )
    vel = np.zeros( Npoints )
    # Assign initial position and velocity
    pos[ 0 ] = x0 # First element of position array is whatever user gave as initial position
    vel[ 0 ] = v0 # First element of velocity array is whatever user gave as initial velocity

    # Main integration loop
    for i in range( 0 , Npoints - 1 ):
        # Find the Right-Hand-Side (RHS) -> the derivatives of position and velocity at the "current" moment "i"
        rhs_pos, rhs_vel = rhs_oscillator( pos[ i ] , vel[ i ] )
        # Complete first half-step forward in velocity
        v_half = vel[ i ] + rhs_vel*dt/2.0
        # Find the Right-Hand-Side (RHS) -> the derivatives of position and velocity at the half-step
        rhs_pos, rhs_vel = rhs_oscillator( pos[ i ] , v_half )
        # Complete full-step forward in position
        pos[ i + 1 ] = pos[ i ] + rhs_pos*dt
        # Find the Right-Hand-Side (RHS) -> the derivatives of position and velocity at the "next" moment "i+1" for position
        rhs_pos, rhs_vel = rhs_oscillator( pos[ i + 1 ] , v_half )
        # Complete second half-step forward in velocity
        vel[ i + 1 ] = v_half + rhs_vel*dt/2.0

    return time, pos, vel

# Right-Hand-Side for the ballistic trajectory
# Inputs:
# - beta: drag coefficient (Stokes drag) [kg/sec]
# - mass: the mass of the body thrown [kg]
# - pos[ 2 ]: 2D array holding X and Y position [m]
# - vel[ 2 ]: 2D array holding V_X and V_Y velocity [m/sec]
# Outputs:
# - rhs_pos[ 2 ]: RHS of position (Xdot & Ydot) in [m/sec]
# - rhs_vel[ 2 ]: RHS of velocity (V_Xdot & V_Ydot) in [m/sec^2]
def Ballistic_RHS( beta , mass , pos , vel ):

    rhs_pos = [ vel[ 0 ] , # Xdot = Vx
                vel[ 1 ] ] # Ydot = Vy
    rhs_vel = [ - beta*vel[ 0 ]/mass , # VXdot = - beta*VX
                - g_const - beta*vel[ 1 ]/mass ] # VYdot = - g - beta*VY

    # Don't forget to convert to Numpy arrays before returning
    return np.array( rhs_pos ), np.array( rhs_vel )


# 2D Verlet integrator
# Inputs:
# - pos_0[ 2 ]: Initial position ( X0 , Y0 ) [m]
# - vel_0[ 2 ]: Initial velocity ( V0 [m/sec] , alpha [deg] )
# NOTE: V0 is magnitude, alpha is the angle above the horizon - you have to convert! 
# - body_param[ 2 ]: Body parameters ( mass [kg] , beta [kg/sec] )  
# - sim_param[ 3 ]: Simulation parameters ( t_i , t_f , Npoints )
# -- t_i: initial time [sec]
# -- t_f: final time [sec]
# -- Npoints: number of points [-]
# Outputs:
# - time[ Npoints ]: time array [sec]
# - pos[ Npoints ][ 2 ]: position array ( X , Y ) for each time point [m]
# - vel[ Npoints ][ 2 ]: velocity array ( V_X , V_Y ) for each time point [m/sec]
def Verlet_2D( pos_0 , vel_0 , body_param , sim_param ):

    # Take out the body parameters
    mass = body_param[ 0 ]
    beta = body_param[ 1 ]

    # Assign the initial, final and Npoints values
    t_i = sim_param[ 0 ]
    t_f = sim_param[ 1 ]
    Npoints = sim_param[ 2 ]
    # Compute time step 
    # |  |  |  | -> intervals are always 1 less than the points
    dt = ( t_f - t_i )/( Npoints - 1.0 ) 
    # Create the time array
    time = np.linspace( t_i , t_f , Npoints )

    # Initialize the vectors which will hold the solution
    pos = np.zeros( ( Npoints , 2 ) ) # pos[ 0 ] is [ X( 0 ) , Y( 0 ) ]  ,
    # pos[ i ] is [ X[ i ] , Y[ i ] ]
    vel = np.zeros( ( Npoints , 2 ) ) # vel[ 0 ] is [ VX( 0 ) , VY( 0 ) ] 

    # Convert and assign the initial position and velocity
    pos[ 0 ][ 0 ] = pos_0[ 0 ] # Vx0 = whatever was given as input
    pos[ 0 ][ 1 ] = pos_0[ 1 ] # Vy0 = whatever was given as input
    # Vx0 = V0*cos( alpha ) -> converted to radians
    vel[ 0 ][ 0 ] = vel_0[ 0 ]*np.cos( vel_0[ 1 ]*np.pi/180.0 ) 
    # Vy0 = V0*sin( alpha ) -> converted to radians
    vel[ 0 ][ 1 ] = vel_0[ 0 ]*np.sin( vel_0[ 1 ]*np.pi/180.0 ) 

    # Main integration loop
    for i in range( 0 , Npoints - 1 ):
        # Call RHS function to get the forces in the current point "i"
        rhs_pos, rhs_vel = Ballistic_RHS( beta , mass , pos[ i ] , vel[ i ] )
        # Compute the first half-step velocity
        vel_half = vel[ i ] + rhs_vel*dt/2.0
        # Call RHS function to get the forces in the "half-point"
        rhs_pos, rhs_vel = Ballistic_RHS( beta , mass , pos[ i ] , vel_half )
        # Compute the full step position in the future
        pos[ i + 1 ] = pos[ i ] + rhs_pos*dt
        # Call RHS function to get the forces in the "next" point "i+1"
        rhs_pos, rhs_vel = Ballistic_RHS( beta , mass , pos[ i + 1 ] , vel_half )
        # Compute the second half-step velocity
        vel[ i + 1 ] = vel_half + rhs_vel*dt/2.0
        if pos[ i + 1 ][ 1 ] < 0.0:
            # If my next position in Y is < 0 (I go underground), stop me on the ground
            # Plastic collision
            #pos[ i + 1 ][ 1 ] = 0.0
            #vel[ i + 1 ][ 1 ] = 0.0
            # Ellastic collision
            #pos[ i + 1 ][ 1 ] = 0.0 # Assume first point bellow 0 is where I cross
            #vel[ i + 1 ][ 1 ] *= - 1.0 # "flip" Y velocity to reflect
            # Realistic collision
            pos[ i + 1 ][ 1 ] = 0.0
            vel[ i + 1 ][ 1 ] *= - 0.9

    return time, pos, vel


# Right-Hand-Side for the ballistic trajectory
# Inputs:
# - beta: drag coefficient (Stokes drag) [kg/sec]
# - mass: the mass of the body thrown [kg]
# - pos[ 3 ]: 3D array holding X and Y and Z position [m]
# - vel[ 3 ]: 3D array holding V_X and V_Y and V_Z velocity [m/sec]
# Outputs:
# - rhs_pos[ 3 ]: RHS of position (Xdot & Ydot & Zdot) in [m/sec]
# - rhs_vel[ 3 ]: RHS of velocity (V_Xdot & V_Ydot & V_Zdot) in [m/sec^2]
def Ballistic_RHS_3D( beta , mass , pos , vel ):

    rhs_pos = [ vel[ 0 ] , # Xdot = Vx
                vel[ 1 ] , # Ydot = Vy
                vel[ 2 ] ] # Zdot = Vz
    rhs_vel = [ - beta*vel[ 0 ]/mass , # VXdot = - beta*VX
                - g_const - beta*vel[ 1 ]/mass , # VYdot = - g - beta*VY
                - beta * vel[2] / mass ] # VZdot = -beta*VZ

    # Don't forget to convert to Numpy arrays before returning
    return np.array( rhs_pos ), np.array( rhs_vel )


# 3D Verlet integrator
# Inputs:
# - pos_0[3]: Initial position (X0, Y0, Z0) [m]
# - vel_0[3]: Initial velocity parameters
#      vel_0[0]: V0 (velocity magnitude) [m/sec]
#      vel_0[1]: alpha (elevation angle above the horizon) [deg]
#      vel_0[2]: phi (azimuth angle in horizontal plane from X-axis) [deg]
#      NOTE: You must convert angles from degrees to radians inside the code!
# - body_param[2]: Body parameters (mass [kg], beta [kg/sec])
# - sim_param[3]: Simulation parameters (t_i, t_f, Npoints)
#      t_i: initial time [sec]
#      t_f: final time [sec]
#      Npoints: number of time points [-]
# Outputs:
# - time[Npoints]: time array [sec]
# - pos[Npoints][3]: position array (X, Y, Z) for each time point [m]
# - vel[Npoints][3]: velocity array (V_X, V_Y, V_Z) for each time point [m/sec]
def Verlet_3D( pos_0 , vel_0 , body_param , sim_param ):

    # Take out the body parameters
    mass = body_param[ 0 ]
    beta = body_param[ 1 ]

    # Assign the initial, final and Npoints values
    t_i = sim_param[ 0 ]
    t_f = sim_param[ 1 ]
    Npoints = sim_param[ 2 ]
    # Compute time step 
    # |  |  |  | -> intervals are always 1 less than the points
    dt = ( t_f - t_i )/( Npoints - 1.0 ) 
    # Create the time array
    time = np.linspace( t_i , t_f , Npoints )

    # Initialize the vectors which will hold the solution
    pos = np.zeros( ( Npoints , 3 ) ) # pos[ 0 ] is [ X( 0 ) , Y( 0 ) , Z (0)]  ,
    # pos[ i ] is [ X[ i ] , Y[ i ] , Z(i)]
    vel = np.zeros( ( Npoints , 3 ) ) # vel[ 0 ] is [ VX( 0 ) , VY( 0 ) , VZ (0) ] 

    # Convert and assign the initial position and velocity
    pos[ 0 ][ 0 ] = pos_0[ 0 ] # Vx0 = whatever was given as input
    pos[ 0 ][ 1 ] = pos_0[ 1 ] # Vy0 = whatever was given as input
    pos[ 0 ][ 2 ] = pos_0[ 2 ] # Vz0 = whatever was given as input
    # Vx0 = V0 * cos(alpha) * cos(phi), converted to radians
    vel[0][0] = vel_0[0] * np.cos(vel_0[1] * np.pi / 180.0) * np.cos(vel_0[2] * np.pi / 180.0)
    # Vy0 = V0 * sin(alpha), converted to radians
    vel[0][1] = vel_0[0] * np.sin(vel_0[1] * np.pi / 180.0)
    # Vz0 = V0 * cos(alpha) * sin(phi), converted to radians
    vel[0][2] = vel_0[0] * np.cos(vel_0[1] * np.pi / 180.0) * np.sin(vel_0[2] * np.pi / 180.0)

    # Main integration loop
    for i in range( 0 , Npoints - 1 ):
        # Call RHS function to get the forces in the current point "i"
        rhs_pos, rhs_vel = Ballistic_RHS_3D( beta , mass , pos[ i ] , vel[ i ] )
        # Compute the first half-step velocity
        vel_half = vel[ i ] + rhs_vel*dt/2.0
        # Call RHS function to get the forces in the "half-point"
        rhs_pos, rhs_vel = Ballistic_RHS_3D( beta , mass , pos[ i ] , vel_half )
        # Compute the full step position in the future
        pos[ i + 1 ] = pos[ i ] + rhs_pos*dt
        # Call RHS function to get the forces in the "next" point "i+1"
        rhs_pos, rhs_vel = Ballistic_RHS_3D( beta , mass , pos[ i + 1 ] , vel_half )
        # Compute the second half-step velocity
        vel[ i + 1 ] = vel_half + rhs_vel*dt/2.0
        if pos[ i + 1 ][ 1 ] < 0.0:
            # If my next position in Y is < 0 (I go underground), stop me on the ground
            # Plastic collision
            #pos[ i + 1 ][ 1 ] = 0.0
            #vel[ i + 1 ][ 1 ] = 0.0
            # Ellastic collision
            #pos[ i + 1 ][ 1 ] = 0.0 # Assume first point bellow 0 is where I cross
            #vel[ i + 1 ][ 1 ] *= - 1.0 # "flip" Y velocity to reflect
            # Realistic collision
            pos[ i + 1 ][ 1 ] = 0.0
            vel[ i + 1 ][ 1 ] *= - 0.9

    return time, pos, vel