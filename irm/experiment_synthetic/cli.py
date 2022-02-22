""" Command line parser for IRM """

import argparse
import sys
from pathlib import Path
import datetime as dt
import multiprocessing as mp

import toml

from .main import run_experiment


class IRMRunner(object):
    """Run commands"""

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Pretends to be git",
            usage="""irm <command> [<args>]

Available commands:
   from_params    Parse arguments from the command line.
   from_file      Read a toml config file.
""",
        )
        parser.add_argument("command", help="Subcommand to run")
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print("Unrecognized command")
            parser.print_help()
            sys.exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def from_params(self):
        """Using the original command line args."""
        parser = argparse.ArgumentParser(
            description="""Invariant regression. Parameters {Description (type: default_value)}""",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "--dim",
            type=int,
            default=10,
            help="Dimension (number of variables in X) (int: %(default)d)",
        )
        parser.add_argument(
            "--n_samples", type=int, default=1000, help=" (int: %(default)s)"
        )
        parser.add_argument("--n_reps", type=int, default=10)
        parser.add_argument("--skip_reps", type=int, default=0)
        parser.add_argument(
            "--seed", type=int, default=0, help="Negative is random (int: %(default)d)"
        )  # Negative is random
        parser.add_argument(
            "--print_vectors", type=int, default=1, help="(int: %(default)d)"
        )
        parser.add_argument(
            "--n_iterations", type=int, default=100000, help="(int: %(default)d)"
        )
        parser.add_argument("--lr", type=float, default=1e-3)
        parser.add_argument("--verbose", type=int, default=0, help="(int: %(default)d)")
        parser.add_argument(
            "--methods",
            type=str,
            default="ERM,ICP,IRM",
            help="One or more algorithms (choice from default: str: %(default)s)",
        )
        parser.add_argument(
            "--alpha", type=float, default=0.05, help="(float: %(default)f)"
        )
        parser.add_argument(
            "--env_list", type=str, default=".2,2.,5.", help="(str: %(default)s)"
        )
        parser.add_argument(
            "--setup_sem", type=str, default="chain", help="(str: %(default)s)"
        )
        parser.add_argument(
            "--setup_ones", type=int, default=1, help="(int: %(default)d)"
        )
        parser.add_argument(
            "--setup_hidden", type=int, default=0, help="(int: %(default)d)"
        )
        parser.add_argument(
            "--setup_hetero", type=int, default=0, help="(int: %(default)d)"
        )
        parser.add_argument(
            "--setup_scramble", type=int, default=0, help="(int: %(default)d)"
        )
        parser.add_argument(
            "--n_threads", type=int, default=mp.cpu_count(), help="(int: %(default)d)"
        )
        parser.add_argument(
            "--irm_epoch_size",
            type=int,
            default=1000,
            help="Number of iterations between each csv train save (int: %(default)d)",
        )
        parser.add_argument(
            "--irm_cuda",
            default=False,
            action="store_true",
            help="Wether IRM should be performed on the GPU (bool: %(default)d)",
        )
        parser.add_argument("--dump_config", default=False, action="store_true")
        # now that we're inside a subcommand, ignore the first
        # TWO argv s, ie the command and the subcommand
        args = dict(vars(parser.parse_args(sys.argv[2:])))

        if args["dump_config"]:
            _config_dest = f"irm_config_{str(dt.datetime.now()).split('.')[0].replace(' ', '_')}.toml"
            if Path(_config_dest).resolve().exists():
                # avoid overwritting existing config files
                raise FileExistsError("Config file already exists, aborting")
            with open(_config_dest, "w", encoding="utf-8") as _c_f:
                toml.dump(args, _c_f)

        print(f"Running IRM simulation from params: {args}")
        run_experiment(args)

    def from_file(self):
        """Read the configuration params from a config parser."""
        parser = argparse.ArgumentParser(
            description="Read a toml configuration file to parse arguments for simulations"
        )
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument(
            "config_file",
            type=lambda p: Path(p).resolve(),
            help="""
            A toml configuration file. See https://toml.io/en/

            For the parameters' keys and values, run:
                irm from_params --help
""",
        )
        args = parser.parse_args(sys.argv[2:])
        with open(args.config_file, "r", encoding="utf-8") as config:
            params = toml.load(config)

        print(
            f"Running IRM simulation from config file {args.config_file} \nwith params:\n {params}"
        )
        run_experiment(params)


if __name__ == "__main__":
    IRMRunner()
