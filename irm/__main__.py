""" Main CLI for running synthetic IRM experiments"""

from .experiment_synthetic.cli import IRMRunner


def main():
    """Call the IRM automated runner"""
    IRMRunner()


if __name__ == "__main__":
    main()
