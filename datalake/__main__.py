import argparse

class ArgumentError(Exception):
    def __init__(self, message):            
        super().__init__(message)

def main():
    parser = argparse.ArgumentParser(prog='Pipelines',
                                     description="A data engineering programming exercise",
                                     epilog='Either run a pipeline or show dashboard'
                                    )

    parser.add_argument("-n", "--name", type=lambda x: x.lower(), choices=["yelp"], help="specify the name of the pipeline you want to run")
    parser.add_argument("-o", "--option", type=lambda x: x.lower(), choices=["clean", "aggregate", "load"], help="specify the option for pipeline to `clean`, `aggregate` or, `load` the dataset")
    args = parser.parse_args()
    match args.__dict__:
        # ======================================================================
        case {'name': 'yelp', 'option': args.option}:
            """
                Run pipeline to load, clean and aggregate data
            """
            from datalake.pipelines.yelp import pipeline
            pipeline(args.option)
        case _:
            raise ArgumentError("wrong combination of options selected !!!")

if __name__ == "__main__":
    main()

