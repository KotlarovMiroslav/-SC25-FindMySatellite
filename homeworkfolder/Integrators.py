import numpy as np

# Constants of the spring (can be added as function parameters)
k = 1.0 # Spring constant [N/m]
m = 1.0 # Mass [kg]
g_const = 9.81

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

    # RHS for basllistic trajectory
    # Inputs:
    # beta: drag coefficient (stokes) [kg/sec]
    # pos[ 2 ]: 2d array holding x and y position [m]
    # vel[ 2 ]: 2d array holding vx and vy velocity [m/sec]
    # 
    # Outputs:
    # rhs_pos[ 2 ]: rhs of position (xdor and ydot) in [m/sec]
    # rhs_vel[ 2 ]: rhs of velocity {vxdot and vydot} in [m/sec^2]

def Ballistic_RHS( beta , mass , pos , vel ):

    rhs_pos = [ vel[ 0 ] ,
                vel[ 1 ] ]
    rhs_vel = [ - beta*vel[ 0 ]/mass ,
                -g_const - beta*vel[ 1 ]/mass ]
    
    return np.array( rhs_pos ) , np.array( rhs_vel )

    # 2D Verlet integrator
    # Inputs:
    # pos_0[ 2 ]: Initial position ( X0 , Y0 ) [m]
    # vel_0[ 2 ]: Initial velocity ( V0 [m/sec] , alpha [deg] )
    # body_param[ 2 ]: Body parameters ( mass [kg] , beta [kg/sec] )
    # sim_param[ 3 ]: Simulation parameters ( t_i , t_f , Npoints )
    # t_i: intial time [sec]
    # t_f: final time [sec]
    # Npoints: number of points
    #
    # Outputs:
    # time
    # pos
    # vel

def Verlet_2D( pos_0 , vel_0 , body_param , sim_param ):

    mass = body_param[ 0 ]
    beta = body_param[ 1 ]

    t_i = sim_param[ 0 ]
    t_f = sim_param[ 1 ]
    Npoints = sim_param[ 2 ]

    dt = ( t_f - t_i )/( Npoints - 1.0 ) 
    time = np.linspace( t_i , t_f , Npoints )

    pos = np.zeros( ( 2 , Npoints ) ) # pos0 is x, pos1 is y
    vel = np.zeros( ( 2 , Npoints ) ) # vel0 is x, vel1 is y

    pos[ 0 ][ 0 ] = pos_0[ 0 ] # Vx0 = 0
    pos[ 1 ][ 0 ] = pos_0[ 1 ] # Vy0 = 0

    vel[ 0 ][ 0 ] = vel_0[ 0 ]*np.cos( vel_0[ 1 ]*np.pi/180.0) # Vx0 = 0
    vel[ 1 ][ 0 ] = vel_0[ 1 ]*np.sin( vel_0[ 1 ]*np.pi/180.0) # Vy0 = 0

    for i in range(0, Npoints - 1):
        rhs_pos, rhs_vel = Ballistic_RHS(beta, mass, pos[:, i], vel[:, i])
        vel_half = vel[:, i] + rhs_vel*dt/2.0

        rhs_pos, rhs_vel = Ballistic_RHS(beta, mass, pos[:, i], vel_half)
        pos[:, i + 1] = pos[:, i] + rhs_pos*dt

        rhs_pos, rhs_vel = Ballistic_RHS(beta, mass, pos[:, i + 1], vel_half)
        vel[:, i + 1] = vel_half + rhs_vel*dt/2.0


    return time , pos , vel