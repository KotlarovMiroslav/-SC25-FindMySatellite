from Integrators import *
import matplotlib.pyplot as plt
from numpy import pi
import numpy as np

if __name__ == "__main__":

    '''
    # Parameters for calling the Euler integrator
    x0 = 1.0 # initial position
    v0 = 0.0 # initial velocity
    t_i = 0.0 # Initial time
    t_f = 4.0*np.pi # Final time
    Npoints = 10000 # Number of points

    # Call the Euler integrator with the needed inputs and record the outptus
    time, pos_E, vel_E = Euler_Solver( x0 , v0 , t_i , t_f , Npoints )

    # Call the Verlet integrator with the needed inputs and record the outptus
    time, pos_V, vel_V = Verlet_Solver( x0 , v0 , t_i , t_f , Npoints )

    # The real solution which we know because it's analytically solvable
    real_pos = np.cos( time )

    # Make a plot comparing the two
    fig, ax = plt.subplots( )

    plt.plot( time , real_pos , color = "green" , label = "Real" , linewidth = 2 )
    plt.scatter( time , pos_E , color = "red" , label = "Euler" , linewidth = 2 )
    plt.scatter( time , pos_V , color = "blue" , label = "Verlet" , linewidth = 2 )
    
    plt.grid( )
    plt.xlabel( "Time [sec]" )
    plt.ylabel( "Position [m]" )
    plt.legend( loc = "lower right" )
    plt.show( )

    # Make a plot with the error
    fig, ax = plt.subplots( )
    err_E = np.zeros( len( time ) )
    err_V = np.zeros( len( time ) )

    for i in range( 0 , len( time ) ):
        # Compute relative error point by point in [%]
        err_E[ i ] = abs( ( real_pos[ i ] - pos_E[ i ] )/real_pos[ i ] ) * 100.0
        err_V[ i ] = abs( ( real_pos[ i ] - pos_V[ i ] )/real_pos[ i ] ) * 100.0

    plt.plot( time , err_E , color = "red" , label = "Euler Error" , linewidth = 2 )
    plt.plot( time , err_V , color = "blue" , label = "Verlet Error" , linewidth = 2 )

    
    plt.grid( )
    plt.xlabel( "Time [sec]" )
    plt.ylabel( "Position Error [%]" )
    plt.legend( loc = "lower right" )
    plt.yscale( "log" )
    plt.show( )
    '''
    # Assign the parameters to the problem
    pos_0 = [ 0 , 0 , 0] # Initial position
    vel_0 = [ 2.0 ,  # [m/sec] magnitude 
              30.0 , # Elevation Angle [deg]
              0.0 ] # Azimuth Angle [deg]
    body_param = [ 1.0 , # Mass [kg]
                    0.3 ] # Beta [kg/sec] -> 0 means NO DRAG
    sim_param = [ 0.0 , # Initial time [sec]
                  3.0 , # Final time [sec]
                  10000 ] # Number of points

    '''# Call the solver 
    time, pos, vel = Verlet_2D( pos_0 , vel_0 , body_param , sim_param )

    v_x_0 = vel_0[ 0 ]*np.cos( vel_0[ 1 ]*np.pi/180.0 )
    v_y_0 = vel_0[ 0 ]*np.sin( vel_0[ 1 ]*np.pi/180.0 )
    # Real solution in case of beta = 0
    pos_x_r = v_x_0*time + pos_0[ 0 ]
    pos_y_r = v_y_0*time + pos_0[ 1 ] - 0.5*g_const*time*time 
    for i in range( 0 , len( pos_y_r ) ):
        # If any point is underground: keep it on the ground
        if pos_y_r[ i ] < 0.0:
            pos_y_r[ i ] = 0.0
    '''

    # Call the solver 
    time, pos, vel = Verlet_3D( pos_0 , vel_0 , body_param , sim_param )

    # Decompose initial velocity into components using elevation (alpha) and azimuth (phi)
    v_x_0 = vel_0[0] * np.cos(vel_0[1] * np.pi / 180.0) * np.cos(vel_0[2] * np.pi / 180.0)
    v_y_0 = vel_0[0] * np.sin(vel_0[1] * np.pi / 180.0)
    v_z_0 = vel_0[0] * np.cos(vel_0[1] * np.pi / 180.0) * np.sin(vel_0[2] * np.pi / 180.0)

    # Real (analytical) solution in case beta = 0 (no drag)
    pos_x_r = v_x_0 * time + pos_0[0]
    pos_y_r = v_y_0 * time + pos_0[1] - 0.5 * g_const * time**2
    pos_z_r = v_z_0 * time + pos_0[2]  # No gravity assumed in Z

    # Keep the projectile on the ground (Y = 0) if it goes underground
    for i in range(len(pos_y_r)):
        if pos_y_r[i] < 0.0:
            pos_y_r[i] = 0.0

    # Make a plot comparing the two
    fig, ax = plt.subplots( )

    plt.plot( pos_x_r , pos_y_r , color = "green" , label = r"Real, $\beta = 0$" , linewidth = 2 )
    plt.scatter( np.transpose( pos )[ 0 ] , np.transpose( pos )[ 1 ] , color = "red" , label = "Verlet" , linewidth = 2 )

    plt.grid( )
    plt.xlabel( "Position X [m]" )
    plt.ylabel( "Position Y [m]" )
    plt.legend( loc = "lower right" )
    plt.show( )