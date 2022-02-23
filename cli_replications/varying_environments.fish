# WARNING : THIS PROGRAM TAKES A LONG TIME TO RUN

# Fix the settings
set one 1 # fixed coeffiecients to 1
set hidden 1 # Add an aditional hidden confounder variable
set scramble 1 # Scramble using an ortogonal matrix
set hetero 1 # Make the simulation heteroscedastic (most problems are?)
# Basically we want to reproduce the most challenging
# and perhaps most common scenario in regression.

# varying forms of setup
set original_permutations '.2,2.,5.' '5.,.2,2.' '2.,5.,.2'

set permutations_4 '.1,3.5,6.,.476' '3.5,6.,.476,.1' '.1,6.,.476,3.5' '.1,.476,3.5,6.'

set permutations_5 '.15,3.,4.5,2.7,.576'
set -a permutations_5 '3.,4.5,2.7,.576,.15'
set -a permutations_5 '4.5,2.7,.576,.15,3.'
set -a permutations_5 '2.7,.576,.15,3.,4.5'
set -a permutations_5 '.576,.15,3.,4.5,2.7'

set permutations_6 '.234,3.567,2.432,7.,1.1,1.618033988749'
set -a permutations_6 '3.567,2.432,7.,1.1,1.618033988749,.234'
set -a permutations_6 '2.432,7.,1.1,1.618033988749,.234,3.567'
set -a permutations_6 '7.,1.1,1.618033988749,.234,3.567,2.432'
set -a permutations_6 '1.1,1.618033988749,.234,3.567,2.432,7.'
set -a permutations_6 '1.618033988749,.234,3.567,2.432,7.,1.1'

set permutations_7 '2.34,5.673,4.322,.7,3.14159265,1.618033988749,.05'
set -a permutations_7 '5.673,4.322,.7,3.14159265,1.618033988749,.05,2.34'
set -a permutations_7 '4.322,.7,3.14159265,1.618033988749,.05,2.34,5.673'
set -a permutations_7 '.7,3.14159265,1.618033988749,.05,2.34,5.673,4.322'
set -a permutations_7 '3.14159265,1.618033988749,.05,2.34,5.673,4.322,.7'
set -a permutations_7 '1.618033988749,.05,2.34,5.673,4.322,.7,3.14159265'
set -a permutations_7 '.05,2.34,5.673,4.322,.7,3.14159265,1.618033988749'

set permutations_8 '.1,3.5,.2,2.,5.,6.,.476,1.618033988749'
set -a permutations_8 '3.5,.2,2.,5.,6.,.476,1.618033988749,.1'
set -a permutations_8 '.2,2.,5.,6.,.476,1.618033988749,.1,3.5'
set -a permutations_8 '2.,5.,6.,.476,1.618033988749,.1,3.5,.2'
set -a permutations_8 '5.,6.,.476,1.618033988749,.1,3.5,.2,2.'
set -a permutations_8 '6.,.476,1.618033988749,.1,3.5,.2,2.,5.'
set -a permutations_8 '.476,1.618033988749,.1,3.5,.2,2.,5.,6.'
set -a permutations_8 '1.618033988749,.1,3.5,.2,2.,5.,6.,.476'

# vv -> This grid takes about 10 hours
#set param_grid permutations_5 permutations_6 permutations_7
# vv -> This grid takes about 7 hours
#set param_grid original_permutations permutations_4 permutations_8
# vv -> Therefore this grid will probably take ~17 hours
set param_grid original_permutations permutations_4 permutations_5 permutations_6 permutations_7 permutations_8

# Iterate over number of environments
for param in $param_grid
    set publish_dir $param
    mkdir $publish_dir
    cd $publish_dir
    set sub_param $$param
    # Iterate over permutations of a given env. size
    for grid_num in (seq (count $sub_param))
        mkdir $grid_num
        cd $grid_num
        #echo $sub_param[$grid_num] >config.txt # this line was used for debug
        time irm from_params --dump_config --n_threads 8 --n_iterations 20000 --irm_epoch_size 50\
 --setup_ones $one --setup_hidden $hidden --setup_hetero $hetero --setup_scramble $scramble\
 --methods IRM --env_list $sub_param[$grid_num]
        # Here $sub_param[$grid_num] does the magic,
        # passing each one of the elements of the list 
        # of environments defined in $param_grid
        cd ..
    end
    cd ..
end
