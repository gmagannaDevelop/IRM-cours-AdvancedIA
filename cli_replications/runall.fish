
# These are the settings used to create the figure shown
# in the original paper
set setup_ones 1
set setup_hidden 0 1
set setup_scramble 0 1
set setup_hetero 0 1

# This cartesian product generates all possible combinations of parameters
set param_grid $setup_ones'|'$setup_hidden'|'$setup_scramble'|'$setup_hetero

# We loop over the powerset, creating a directory to store the results for each configuration
for param in $param_grid
    set param_ls (string split '|' $param)
    set one $param_ls[1]
    set hidden $param_ls[2]
    set scramble $param_ls[3]
    set hetero $param_ls[4] 
	set publish_dir "ones$one:hidden$hidden:scramble$scramble:hetero$hetero"
    mkdir $publish_dir
    cd $publish_dir
    irm from_params --dump_config --n_threads 16\
        --setup_ones $one --setup_hidden $hidden --setup_hetero $hetero --setup_scramble $scramble
    cd ..
end