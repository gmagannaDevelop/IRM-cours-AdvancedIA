
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
set permutations_8 '.1,3.5,.2,2.,5.,6.,.476,1.618033988749'
set -a permutations_8 '3.5,.2,2.,5.,6.,.476,1.618033988749,.1'
set -a permutations_8 '.2,2.,5.,6.,.476,1.618033988749,.1,3.5'
set -a permutations_8 '2.,5.,6.,.476,1.618033988749,.1,3.5,.2'
set -a permutations_8 '5.,6.,.476,1.618033988749,.1,3.5,.2,2.'
set -a permutations_8 '6.,.476,1.618033988749,.1,3.5,.2,2.,5.'
set -a permutations_8 '.476,1.618033988749,.1,3.5,.2,2.,5.,6.'
set -a permutations_8 '1.618033988749,.1,3.5,.2,2.,5.,6.,.476'

set param_grid permutations_4 permutations_8 original_permutations

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
        cd ..
    end
    cd ..
end
